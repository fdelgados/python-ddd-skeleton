from typing import Optional


class Error:
    def __init__(self, code: int, message: str, details: Optional[str] = ""):
        self._code = code
        self._message = message
        self._details = details

    @property
    def code(self) -> int:
        return self._code

    @property
    def message(self) -> str:
        return self._message

    @property
    def details(self) -> Optional[str]:
        return self._details

    def __eq__(self, other):
        if not isinstance(other, Error):
            return False

        return other.code == self.code

    def __str__(self):
        return f"{self._message}. {self._details}"
