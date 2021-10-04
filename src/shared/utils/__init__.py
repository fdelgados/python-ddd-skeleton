import re


def class_fullname(obj: object) -> str:
    _class = obj.__class__
    module = _class.__module__
    name = _class.__qualname__
    if module is not None and module != "__builtin__":
        name = f"{module}.{name}"

    return name


def camel_to_snake_case(camel_case_string: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", "_", camel_case_string).lower()


def snake_to_camel_case(snake_case_string: str, capitalize: bool = False) -> str:
    components = snake_case_string.split("_")

    camel_case_string = components[0] + "".join(x.title() for x in components[1:])

    if capitalize:
        return camel_case_string.title()

    return camel_case_string
