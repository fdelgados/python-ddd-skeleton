from datetime import datetime


class StoredEvent:
    def __init__(
        self,
        event_body: str,
        event_id: int,
        occurred_on: datetime,
        type_name: str,
    ):
        self._event_body = event_body
        self._event_id = event_id
        self._occurred_on = occurred_on
        self._type_name = type_name

    @property
    def event_body(self) -> str:
        return self._event_body

    @property
    def event_id(self) -> int:
        return self._event_id

    @property
    def occurred_on(self) -> datetime:
        return self._occurred_on

    @property
    def type_name(self) -> str:
        return self._type_name
