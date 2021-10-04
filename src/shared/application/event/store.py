from shared.utils import class_fullname
from shared.domain.bus.event import DomainEvent, DomainEventSubscriber, EventStore
import shared.infrastructure.environment.globalvars as glob


class StoreDomainEventOnPublished(DomainEventSubscriber):
    def handle(self, domain_event: DomainEvent) -> None:
        domain_event_class_name = class_fullname(domain_event)
        context, _ = domain_event_class_name.split(".", maxsplit=1)

        if not glob.settings.is_event_store_enabled_for_context(context):
            return None

        event_store = glob.container.get(glob.settings.event_store_id(context))

        if not event_store or not isinstance(event_store, EventStore):
            return None

        event_store.append(domain_event)

        return None
