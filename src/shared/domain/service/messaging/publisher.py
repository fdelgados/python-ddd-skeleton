import abc
from shared.domain.event.event import DomainEvent


class EventPublisher(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def publish(self, event: DomainEvent, publisher: str) -> None:
        raise NotImplementedError
