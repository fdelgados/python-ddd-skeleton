import abc
from shared.domain.bus.event import DomainEvent


class AggregateRoot(metaclass=abc.ABCMeta):
    _events = []

    def record_event(self, event: DomainEvent):
        self._events.append(event)

    def pull_events(self):
        events = self._events.copy()
        self._events.clear()

        return events
