#!/usr/bin/env python

import argparse
import os.path
import subprocess
import threading
from typing import Dict, Any
import json
from pika import exceptions

from shared.application.bootstrap import Bootstrap
from shared.infrastructure.logging.file.logger import FileLogger
from shared.domain.service.logging.logger import Logger
from shared.infrastructure.messaging.rabbitmq.connector import RabbitMqConnector

bootstrap = Bootstrap()


def _on_message(ch, method, _, message):
    commands = bootstrap.settings.event_subscribed_commands(
        method.exchange, method.routing_key
    )

    command = commands.get(method.consumer_tag)
    if not command:
        ch.basic_nack(delivery_tag=method.delivery_tag)

    process = subprocess.Popen(
        _build_command(command, message),
        stdout=subprocess.PIPE,
        universal_newlines=True,
    )

    while True:
        output = process.stdout.readline()
        print(output.strip())
        # Do something else
        return_code = process.poll()
        if return_code is not None:
            # print('RETURN CODE', return_code)
            # Process has finished, read rest of the output
            for output in process.stdout.readlines():
                print(output.strip())
            break

    if return_code != 0:
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
    else:
        ch.basic_ack(delivery_tag=method.delivery_tag)


def _build_command(command_name, message):
    executable = os.path.join(os.path.dirname(__file__), "console.py")

    command = ["python", executable, command_name]
    decoded_message = json.loads(message.decode("utf-8"))
    metadata = decoded_message.get("metadata", {})
    body = decoded_message.get("body", {})

    def quote(val: Any):
        chars = [" "]
        if isinstance(val, list):
            val = ",".join(val)

        if any(char in val for char in chars):
            return f'"{val}"'

        return val

    for argument, value in metadata.items():
        command.append(f"--{argument.replace('_', '-')}={quote(value)}")

    for argument, value in body.items():
        if value is None:
            continue

        command.append(f"--{argument.replace('_', '-')}={quote(value)}")

    return command


def consume(exchange_name: str, routing_keys: Dict, logger: Logger, channel) -> None:
    logger.info(" [*] Connecting to server...")

    try:
        channel.exchange_declare(
            exchange=exchange_name, exchange_type="direct", durable=True
        )

        for routing_key, queues in routing_keys.items():
            for queue in queues.items():
                queue_prefix = queue[0]

                queue_name = f"{queue_prefix}.on.{routing_key}"

                result = channel.queue_declare(queue=queue_name, durable=True)
                queue_name = result.method.queue
                channel.queue_bind(
                    queue=queue_name, exchange=exchange_name, routing_key=routing_key
                )

                channel.basic_consume(
                    queue_name,
                    on_message_callback=_on_message,
                    consumer_tag=queue_prefix,
                    auto_ack=False,
                )

        logger.info(" [*] Waiting for messages")

        channel.basic_qos(prefetch_count=1)

        thread = threading.Thread(target=channel.start_consuming)
        thread.start()
    except exceptions.ConnectionClosedByBroker:
        logger.error(" [x] Connection closed by broker")
    except KeyboardInterrupt:
        channel.stop_consuming()
        logger.info(" [*] Consumer stopped")


exchanges = bootstrap.settings.subscribed_events()
connection_settings = bootstrap.settings.rabbit_connection_settings()
file_logger = FileLogger()
connector = RabbitMqConnector(file_logger)

_DEFAULT_ENVIRONMENT = os.environ.get("ENVIRONMENT")

parser = argparse.ArgumentParser(
    description="Run message workers", usage="python build.py", add_help=False
)

parser.add_argument(
    "-e",
    "--environment",
    dest="environment",
    help=f"Environment. Default: {_DEFAULT_ENVIRONMENT}",
    default=_DEFAULT_ENVIRONMENT,
    metavar="",
)

parser.add_argument(
    "-w", "--worker", dest="worker", help="Worker name", default=None, metavar=""
)

parser.add_argument(
    "-h",
    "--host",
    dest="host",
    help=f"Host name. Default: {connection_settings.get('host')}",
    default=connection_settings.get("host"),
    metavar="",
)

parser.add_argument(
    "-p",
    "--port",
    dest="port",
    help=f"Connection port. Default: {connection_settings.get('port')}",
    default=connection_settings.get("port"),
    metavar="",
)

parser.add_argument(
    "-v",
    "--virtual-host",
    dest="virtual_host",
    help=f"Virtual host. Default: {connection_settings.get('vhost', '/')}",
    default=connection_settings.get("vhost", "/"),
    metavar="",
)

args = parser.parse_args()

connection = connector.connect(
    {
        "user": connection_settings.get("user"),
        "password": connection_settings.get("password"),
        "host": args.host,
        "port": args.port,
        "vhost": args.virtual_host,
    }
)
connection_channel = connection.channel()

for subscribed_exchange, listening_routing_keys in exchanges.items():
    consume(
        subscribed_exchange, listening_routing_keys, file_logger, connection_channel
    )
