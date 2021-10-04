import abc

from typing import Any


class Cache(metaclass=abc.ABCMeta):
    TTL_IN_DAYS = 60

    @abc.abstractmethod
    def write(self, key: str, value: str) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def read(self, key: str) -> Any:
        raise NotImplementedError
