from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional
import abc


class QueryError(RuntimeError):
    pass


class QueryNotRegisteredError(QueryError):
    def __init__(self, query: Query) -> None:
        query_class = type(query).__name__

        super().__init__(f"The query <{query_class}> hasn't a query handler associated")


class QueryNotCallableError(QueryError):
    def __init__(self, query: Query) -> None:
        query_class = type(query).__name__

        super().__init__(f"The query <{query_class}> is not callable")


@dataclass(frozen=True)
class Query(metaclass=abc.ABCMeta):
    pass


class QueryHandler(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def handle(self, query: Query) -> Optional[Response]:
        raise NotImplementedError


class Response(metaclass=abc.ABCMeta):
    def to_dict(self) -> Dict:
        properties = {}
        for property_name, value in self.__dict__.items():
            properties[property_name.lstrip("_")] = value

        return properties


class QueryBus(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def ask(self, query: Query) -> Optional[Response]:
        raise NotImplementedError
