from __future__ import annotations
import re
from typing import Optional
from urllib.parse import urlparse


class InvalidUrlException(Exception):
    pass


class Url:
    _URL_PATTERN = r"^http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+$"

    def __init__(self, address: str):
        self._address = None
        self._ensure_is_valid_url(address)

        self._address = address
        self._url_struct = urlparse(self._address)

    def _ensure_is_valid_url(self, address: str):
        if not re.search(self._URL_PATTERN, address):
            raise InvalidUrlException("Invalid Url")

    @property
    def address(self) -> str:
        return self._address

    @property
    def scheme(self) -> Optional[str]:
        return self._url_struct.scheme if self._url_struct.scheme else None

    @property
    def domain(self) -> Optional[str]:
        return self._url_struct.netloc if self._url_struct.netloc else None

    @property
    def path(self) -> Optional[str]:
        return self._url_struct.path if self._url_struct.path else None

    @property
    def params(self) -> Optional[str]:
        return self._url_struct.params if self._url_struct.params else None

    @property
    def query(self) -> Optional[str]:
        return self._url_struct.query if self._url_struct.query else None

    @property
    def fragment(self) -> Optional[str]:
        return self._url_struct.fragment if self._url_struct.fragment else None

    def match(self, pattern: str) -> bool:
        return re.fullmatch(pattern, self.address) is not None

    def __str__(self) -> str:
        return self.address

    def __repr__(self) -> str:
        return "<Url: {}>".format(self.address if self.address else "Invalid URL")

    def __eq__(self, other: Url) -> bool:
        return self.address == other.address

    def __hash__(self):
        return hash(self._address)
