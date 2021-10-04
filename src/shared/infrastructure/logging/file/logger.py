import logging

from typing import Optional

import shared.infrastructure.environment.globalvars as glob
from shared.domain.service.logging.logger import Logger


class FileLogger(Logger):
    def __init__(self, name: Optional[str] = None, logfile: Optional[str] = None):
        settings = glob.settings
        if not name:
            name = settings.site()

        self._name = name
        logger = self._logger

        if not logfile:
            logfile = self._name

        level = logging.DEBUG
        if settings.is_production():
            level = logging.WARNING

        logger.setLevel(level)

        formatter = logging.Formatter("%(asctime)s :: %(levelname)s :: %(message)s")
        file_handler = logging.FileHandler(f"{settings.logs_dir()}/{logfile}.log")
        logging.StreamHandler()
        file_handler.setFormatter(formatter)

        logger.addHandler(file_handler)

    @property
    def _logger(self):
        return logging.getLogger(self._name)

    def debug(self, message: str, *args) -> None:
        self._logger.debug(message, *args)

    def info(self, message: str, *args) -> None:
        self._logger.info(message, *args)

    def warning(self, message: str, *args) -> None:
        self._logger.warning(message, *args)

    def error(self, message: str, *args) -> None:
        self._logger.error(message, *args)

    def critical(self, message: str, *args) -> None:
        self._logger.critical(message, *args)
