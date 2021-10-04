#!/usr/bin/env python

import sys
import argparse

from importlib import util
from typing import List

from shared.infrastructure.command import ConsoleCommand, Input
from shared.application.bootstrap import Bootstrap

boostrap = Bootstrap()


def _parse_input_args(arguments: List):
    input_args = {}
    for argument in arguments:
        argument_name, value = argument.split("=")
        argument_name = argument_name.lstrip("-").replace("-", "_")
        value = value.strip('"')

        input_args[argument_name] = value

    return Input(input_args)


if __name__ == "__main__":

    _DEFAULT_ENVIRONMENT = "development"

    parser = argparse.ArgumentParser()

    parser.add_argument("command", metavar="command:name", type=str)
    parser.add_argument(
        "-e",
        "--environment",
        dest="environment",
        help=f"Environment. Default: {_DEFAULT_ENVIRONMENT}",
        default=_DEFAULT_ENVIRONMENT,
        metavar="",
    )

    args, unknown = parser.parse_known_args()

    command_path = boostrap.settings.command(args.command)

    if not command_path:
        sys.exit("There is no command")

    module_name, class_name = command_path.rsplit(".", 1)
    try:
        spec = util.find_spec(module_name)
        module = util.module_from_spec(spec)
        spec.loader.exec_module(module)

        class_ = getattr(module, class_name)
        command: ConsoleCommand = class_(args.environment)

        sys.exit(command.execute(_parse_input_args(unknown)))

    except (ModuleNotFoundError, AttributeError) as error:
        sys.exit(str(error))
