from __future__ import annotations

from dataclasses import dataclass
import abc


class CommandError(RuntimeError):
    pass


class CommandNotRegisteredError(CommandError):
    def __init__(self, command: Command) -> None:
        command_class = type(command).__name__

        super().__init__(
            f"The command <{command_class}> hasn't a command handler associated"
        )


class CommandNotCallableError(CommandError):
    def __init__(self, command: Command) -> None:
        command_class = type(command).__name__

        super().__init__(f"The command <{command_class}> is not callable")


@dataclass(frozen=True)
class Command(metaclass=abc.ABCMeta):
    pass


class CommandHandler(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def handle(self, command: Command) -> None:
        raise NotImplementedError


class CommandBus(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def dispatch(self, command: Command) -> None:
        raise NotImplementedError
