import json
import pika
from pika import exceptions

import shared.infrastructure.environment.globalvars as glob
from shared.domain.bus.event import EventBus, DomainEvent
from shared.domain.service.logging.logger import Logger
from shared.infrastructure.messaging.rabbitmq.connector import RabbitMqConnector


def _build_message(event: DomainEvent):
    message = {
        "metadata": {"environment": glob.settings.environment()},
        "body": json.loads(event.serialize()),
    }

    return json.dumps(message).encode()


class RabbitMqEventBus(EventBus):
    def __init__(
        self, connector: RabbitMqConnector, exchange_name: str, logger: Logger
    ):
        self._connector = connector
        self._exchange_name = exchange_name
        self._logger = logger

    def _do_publish(self, domain_event: DomainEvent) -> None:
        connection = self._connect()

        try:
            channel = connection.channel()
            channel.exchange_declare(
                exchange=self._exchange_name, exchange_type="direct", durable=True
            )
            channel.basic_publish(
                exchange=self._exchange_name,
                routing_key=domain_event.type_name(),
                body=_build_message(domain_event),
                properties=pika.BasicProperties(delivery_mode=2),
            )
        except (exceptions.AMQPError, ValueError) as error:
            self._logger.error(str(error))

            raise
        finally:
            self._disconnect()

    def _connect(self):
        return self._connector.connect()

    def _disconnect(self):
        self._connector.disconnect()
