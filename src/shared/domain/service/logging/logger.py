import abc


class Logger(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def debug(self, message: str, *args) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def info(self, message: str, *args) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def warning(self, message: str, *args) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def error(self, message: str, *args) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def critical(self, message: str) -> None:
        raise NotImplementedError
