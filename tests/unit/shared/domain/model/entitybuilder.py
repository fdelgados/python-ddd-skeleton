import abc
from typing import Any

from faker import Faker


class EntityBuilder(metaclass=abc.ABCMeta):
    def __init__(self):
        self._fake = Faker()

    @abc.abstractmethod
    def build(self) -> Any:
        raise NotImplementedError

    @property
    def fake(self) -> Faker:
        return self._fake
