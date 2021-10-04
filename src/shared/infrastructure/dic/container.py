import os
import os.path
from typing import List, Dict, Generator, Optional, Any
from importlib import util
from xml.etree import ElementTree
from dependency_injector import containers


def create_container(settings):
    services_files = settings.services_files()
    event_handlers_files = settings.event_handlers_files()

    service_container = containers.DynamicContainer()
    services = _get_services(services_files)
    service_provider_cls = _import_cls("dependency_injector.providers.Factory")

    event_handlers = {}
    actual_services_ids = []
    for service_id, info in services.items():
        if not info.get("alias"):
            continue

        try:
            services[service_id] = services[info.get("alias")]
            actual_services_ids.append(info.get("alias"))
        except KeyError:
            continue

    # TODO check if it is necessary to delete aliased services
    # for actual_services_id in actual_services_ids:
    #     del services[actual_services_id]

    for service_id, info in services.items():
        _create_service(
            services,
            service_container,
            service_provider_cls,
            service_id,
            info,
            settings,
        )

    store_domain_even_subscriber = settings.store_domain_even_subscriber()
    store_domain_even_subscriber_id = store_domain_even_subscriber.get("id")

    service_cls = _import_cls(store_domain_even_subscriber.get("class_name"))
    setattr(
        service_container,
        store_domain_even_subscriber_id.replace(".", "_"),
        service_provider_cls(service_cls),
    )

    if event_handlers_files is not None:
        if isinstance(event_handlers_files, str):
            event_handlers_files = [event_handlers_files]

        for event_handlers_file in event_handlers_files:
            event_handlers.update(_get_event_handlers(event_handlers_file))

        subscriber_instances = {}
        for domain_event, subscriber_data in event_handlers.items():
            subscriber_data["subscribers"].insert(0, store_domain_even_subscriber_id)
            subscriber_instances[domain_event] = {"subscribers": []}
            for subscriber_id in subscriber_data["subscribers"]:
                subscriber = getattr(
                    service_container, subscriber_id.replace(".", "_")
                )()

                subscriber.subscribe_to(domain_event)

                subscriber_instances[domain_event]["subscribers"].append(subscriber)

    class Container:
        @classmethod
        def get(cls, registered_service_id: str) -> Optional[Any]:
            try:
                return getattr(
                    service_container, registered_service_id.replace(".", "_")
                )()
            except AttributeError:
                return None

        @classmethod
        def event_handlers(cls, event_name: str) -> Generator:
            domain_event_subscribers = subscriber_instances.get(event_name, {}).get(
                "subscribers", []
            )

            for domain_event_subscriber in domain_event_subscribers:
                yield domain_event_subscriber

    return Container


def _get_services(services_files: List) -> Dict:
    services = {}

    for services_file in services_files:
        services.update(_get_service_from_file(services_file))

    return services


def _get_service_from_file(services_file: str) -> Dict:
    _ensure_file_exist(services_file)
    _ensure_file_is_valid(services_file)

    services = {}

    tree = ElementTree.parse(services_file)
    root = tree.getroot()

    for service in root:
        if service.tag != "service":
            continue

        if service.attrib.get("alias"):
            services[service.attrib["id"]] = {"alias": service.attrib.get("alias")}

            continue

        service_data = {"class_name": service.attrib["class"], "arguments": []}

        for service_argument in service:
            if service_argument.tag != "argument":
                continue

            service_data["arguments"].append(
                {
                    "type": service_argument.attrib["type"],
                    "name": service_argument.attrib["name"],
                    "value": service_argument.attrib["value"],
                    "args": service_argument.attrib.get("args"),
                }
            )

        services[service.attrib["id"]] = service_data

    return services


def _import_cls(full_class_name: str):
    path_components = full_class_name.split(".")
    class_name = path_components[-1]
    mod = ".".join(path_components[:-1])

    spec = util.find_spec(mod)
    module = util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return getattr(module, class_name)


def _create_service(
    services, service_container, service_provider_cls, service_id: str, info, settings
):
    service_key = service_id.replace(".", "_")
    if hasattr(service_container, service_key):
        return getattr(service_container, service_key)

    service_args = info.get("arguments")
    args = {}

    for argument in service_args:
        if argument.get("type") == "env":
            args[argument["name"]] = os.environ.get(argument["value"])
        elif argument.get("type") == "parameter":
            args[argument["name"]] = argument["value"]
        elif argument.get("type") == "settings":
            method = getattr(settings, argument["value"])
            method_arguments = argument["args"]

            if not method_arguments:
                value = method()
            else:
                value = method(*argument["args"].split(","))

            args[argument["name"]] = value
        elif argument.get("type") == "service":
            dependency_service_id = argument["value"]

            if isinstance(services[dependency_service_id], str):
                dependency_service_id = services[dependency_service_id]

            dependency_service_info = services[dependency_service_id]

            args[argument["name"]] = _create_service(
                services,
                service_container,
                service_provider_cls,
                dependency_service_id,
                dependency_service_info,
                settings,
            )

    service_cls = _import_cls(info.get("class_name"))
    setattr(service_container, service_key, service_provider_cls(service_cls, **args))

    return getattr(service_container, service_key)


def _get_event_handlers(event_handlers_file: str):
    _ensure_file_exist(event_handlers_file)
    _ensure_file_is_valid(event_handlers_file)

    events = {}

    tree = ElementTree.parse(event_handlers_file)
    root = tree.getroot()

    for event in root:
        if event.tag != "event":
            continue

        event_class_name = event.attrib["class"]
        events[event_class_name] = {
            "class": _import_cls(event_class_name),
            "subscribers": [],
        }

        for event_handler in event:
            if event_handler.tag != "handler":
                continue

            events[event_class_name]["subscribers"].append(event_handler.attrib["id"])

    return events


def _ensure_file_exist(services_file: str):
    if not os.path.exists(services_file):
        raise FileNotFoundError("File {} does not exists".format(services_file))


def _ensure_file_is_valid(services_file: str):
    if not services_file.endswith(".xml"):
        raise ValueError("Services file must be an xml file")
