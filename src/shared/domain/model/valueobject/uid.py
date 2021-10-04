from __future__ import annotations

import re
import abc
import uuid


class Uuid(metaclass=abc.ABCMeta):
    __ID_PATTERN = (
        r"[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}$"
    )

    def __init__(self, value: str = None):
        if not value:
            value = str(uuid.uuid4())

        self.__ensure_is_valid_id(value)
        self.__value = value

    def __ensure_is_valid_id(self, value: str):
        regex = re.compile(self.__ID_PATTERN, re.IGNORECASE)
        if not regex.match(value):
            raise ValueError("Invalid {} value".format(type(self).__name__))

    @property
    def value(self) -> str:
        return self.__value

    def __eq__(self, other: Uuid) -> bool:
        if not other:
            return False

        return self.value == other.value

    def __str__(self) -> str:
        return self.value

    def __hash__(self):
        return hash(self.value)

    def __repr__(self):
        return "<{}: {}>".format(type(self).__name__, self.value)
