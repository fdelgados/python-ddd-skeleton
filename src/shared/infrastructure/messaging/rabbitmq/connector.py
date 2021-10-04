from typing import Optional, Dict
import pika
from pika import exceptions
import shared.infrastructure.environment.globalvars as glob
from shared.domain.service.logging.logger import Logger


class RabbitMqConnector:
    def __init__(self, logger: Logger):
        self._logger = logger
        self._connection = None

    def connect(
        self, connection_settings: Optional[Dict] = None
    ) -> pika.BlockingConnection:
        if not connection_settings:
            connection_settings = glob.settings.rabbit_connection_settings()

        credentials = pika.PlainCredentials(
            connection_settings.get("user"), connection_settings.get("password")
        )

        try:
            self._connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=connection_settings.get("host"),
                    port=connection_settings.get("port"),
                    virtual_host=connection_settings.get("vhost", "/"),
                    credentials=credentials,
                )
            )

            return self._connection
        except Exception as error:
            self._logger.error(repr(error))

            raise Exception(repr(error))

    def disconnect(self):
        if not self._connection:
            return

        try:
            self._connection.close()
        except exceptions.ConnectionWrongStateError as error:
            self._logger.warning(str(error))
