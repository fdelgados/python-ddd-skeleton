import abc

from typing import Any, Dict

import shared.infrastructure.environment.globalvars as glob
from shared.infrastructure.dic.container import create_container


class Input:
    def __init__(self, arguments: Dict):
        self._arguments = arguments

    def get_argument(self, name: str, default: Any = None):
        return self._arguments.get(name, default)


class ConsoleCommand(metaclass=abc.ABCMeta):
    def __init__(self, environment: str):
        self._environment = environment
        self._container = create_container(settings)

    @property
    def container(self):
        return self._container

    @property
    def environment(self):
        return self._environment

    @abc.abstractmethod
    def execute(self, input_args: Input) -> int:
        raise NotImplementedError
