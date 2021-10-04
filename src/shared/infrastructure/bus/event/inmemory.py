import multiprocessing

from shared.utils import class_fullname
from shared.domain.bus.event import EventBus, DomainEvent
import shared.infrastructure.environment.globalvars as glob


class InMemoryEventBus(EventBus):
    def _do_publish(self, domain_event: DomainEvent) -> None:
        domain_event_name = class_fullname(domain_event)
        event_handlers = glob.container.event_handlers(domain_event_name)

        jobs = []
        for subscriber in event_handlers:
            if not subscriber.is_subscribed_to(domain_event):
                continue

            process = multiprocessing.Process(
                target=subscriber.handle, args=(domain_event,)
            )
            jobs.append(process)

        for job in jobs:
            job.start()
