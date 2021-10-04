import abc
import json
from datetime import datetime
from typing import List, Dict, Optional, Any


class DomainEvent(metaclass=abc.ABCMeta):
    def __init__(self, aggregate_id: Optional[Any] = None):
        self._occurred_on = datetime.now()
        self._aggregate_id = aggregate_id

    @classmethod
    def type_name(cls):
        module = cls.__module__
        name = cls.__qualname__
        if module is not None and module != "__builtin__":
            name = f"{module}.{name}"

        return name

    @property
    def occurred_on(self):
        return self._occurred_on

    @property
    def aggregate_id(self) -> Optional[Any]:
        return self._aggregate_id

    def serialize(self) -> str:
        def json_converter(o):
            if isinstance(o, datetime):
                return o.__str__()

            return o

        properties = self.__sanitize_property_names()

        return json.dumps(properties, ensure_ascii=False, default=json_converter)

    def __sanitize_property_names(self) -> Dict:
        properties = {}
        for property_name, value in self.__dict__.items():
            properties[property_name.lstrip("_")] = value

        return properties

    def __str__(self) -> str:
        return self.serialize()

    def __repr__(self) -> str:
        return "DomainEvent <{}>".format(type(self).__name__)


class DomainEventSubscriber(metaclass=abc.ABCMeta):
    def __init__(self):
        self._events = []

    def is_subscribed_to(self, domain_event: DomainEvent) -> bool:
        return domain_event.type_name() in self._events

    def subscribe_to(self, domain_event: str) -> None:
        self._events.append(domain_event)

    @abc.abstractmethod
    def handle(self, domain_event: DomainEvent) -> None:
        raise NotImplementedError


class EventBus(metaclass=abc.ABCMeta):
    def publish(self, *domain_events: DomainEvent) -> None:
        for domain_event in domain_events:
            self._do_publish(domain_event)

    @abc.abstractmethod
    def _do_publish(self, domain_event: DomainEvent) -> None:
        raise NotImplementedError


class EventStore(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def append(self, domain_event: DomainEvent) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def events_since(self, domain_event_id: int) -> List[DomainEvent]:
        raise NotImplementedError

    @abc.abstractmethod
    def events_by_type(self, *type_name: str, **kwargs) -> List[DomainEvent]:
        raise NotImplementedError
