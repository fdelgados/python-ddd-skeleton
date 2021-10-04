from typing import List

from shared.domain.bus.event import DomainEvent, EventStore
from shared.infrastructure.persistence.sqlalchemy.dbal import DbalService


class MysqlEventStore(EventStore):
    def __init__(self, db_service: DbalService):
        self._db_service = db_service

    def append(self, domain_event: DomainEvent) -> None:
        sentence = """
            INSERT INTO event_store (occurred_on, event_data, event_name, aggregate_id)
            VALUES (:occurred_on, :event_data, :event_name, :aggregate_id)
        """

        self._db_service.execute(
            sentence,
            occurred_on=domain_event.occurred_on,
            event_data=domain_event.serialize(),
            event_name=domain_event.type_name(),
            aggregate_id=domain_event.aggregate_id,
        )

    def events_since(self, domain_event_id: int) -> List[DomainEvent]:
        pass

    def events_by_type(self, *type_name: str, **kwargs) -> List[DomainEvent]:
        sentence = """
            SELECT id, occurred_on, event_data, event_name, aggregate_id
            FROM event_store
            WHERE event_name IN :type_names
        """

        self._db_service.execute(sentence)
