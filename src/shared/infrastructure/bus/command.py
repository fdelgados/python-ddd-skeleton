from shared.utils import camel_to_snake_case, class_fullname
from shared.domain.bus.command import (
    Command,
    CommandHandler,
    CommandBus,
    CommandNotRegisteredError,
    CommandNotCallableError,
)
import shared.infrastructure.environment.globalvars as glob


class CommandBusImpl(CommandBus):
    def dispatch(self, command: Command) -> None:
        command_fullname = class_fullname(command)
        module, command_name = command_fullname.rsplit(".", maxsplit=1)

        handler_id = "{}.{}_handler".format(module, camel_to_snake_case(command_name))

        command_handler: CommandHandler = glob.container.get(handler_id)

        if not command_handler:
            raise CommandNotRegisteredError(command)

        if not isinstance(command_handler, CommandHandler):
            raise CommandNotRegisteredError(command)

        if not hasattr(command_handler, "handle") or not callable(
            command_handler.handle
        ):
            raise CommandNotCallableError(command)

        command_handler.handle(command)
