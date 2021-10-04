import os
import re
import glob
import collections
from typing import Dict, Any, Optional, List
import toml

from setuptools import find_packages


class Settings:
    def __init__(self, site: str, environment: Optional[str] = "development"):
        self._environment = environment

        if not site:
            raise ValueError("A site name must be provided")

        self._site = site

        configs_dir = "/var/www/config"
        settings_dir = f"{configs_dir}/settings"
        services_dir = f"{configs_dir}/services"
        contexts_dir = "/var/www/src"

        self._contexts = list(
            filter(
                lambda context: "." not in context, find_packages(where=contexts_dir)
            )
        )

        self._config = toml.load(f"{settings_dir}/common/settings.toml")
        common_environment_config = toml.load(
            f"{settings_dir}/common/settings.{self._environment}.toml"
        )

        self._dict_merge(self._config, common_environment_config)

        if not self.is_test():
            country_config = toml.load(f"{settings_dir}/{self._site}/settings.toml")
            self._dict_merge(self._config, country_config)

            country_environment_config = toml.load(
                f"{settings_dir}/{self._site}/settings.{self._environment}.toml"
            )
            self._dict_merge(self._config, country_environment_config)

        self._subscribed_events = {}
        subscribed_events_files = glob.glob(f"{services_dir}/**/subscribed-events.toml")

        for subscribed_events_file in subscribed_events_files:
            self._dict_merge(self._subscribed_events, toml.load(subscribed_events_file))

        self._commands = {}
        commands_files = glob.glob(f"{services_dir}/**/commands.toml")
        for commands_file in commands_files:
            self._dict_merge(self._commands, toml.load(commands_file))

    def _dict_merge(self, dct, merge_dct) -> None:
        for key in merge_dct.keys():
            if (
                key in dct
                and isinstance(dct[key], dict)
                and isinstance(merge_dct[key], collections.abc.Mapping)
            ):
                self._dict_merge(dct[key], merge_dct[key])
            else:
                dct[key] = merge_dct[key]

    def environment(self) -> str:
        return self._environment

    def is_production(self) -> bool:
        return self._environment == "production"

    def is_development(self) -> bool:
        return self._environment == "development"

    def is_test(self) -> bool:
        return self._environment == "test"

    def site(self) -> str:
        return self._site

    def flask_config(self) -> Dict:
        if not self._config.get("flask"):
            return {}

        return {
            key.upper(): value for (key, value) in self._config.get("flask").items()
        }

    def _get(self, section: str, entry: str, default: Optional[Any] = None) -> Any:
        return self._config.get(section).get(entry, default)

    def application_id(self) -> str:
        return self._get("application", "id")

    def api_version(self) -> int:
        return self._get("api", "version")

    def api_title(self) -> str:
        return self._get("api", "title")

    def api_doc_path(self) -> str:
        return self._get("api", "doc_path", "/doc")

    def api_version_str(self) -> str:
        return self._get("api", "version_str").format(self.api_version())

    def api_prefix(self, path: Optional[str] = None) -> str:
        api_prefix = self._get("api", "prefix").format(self.api_version())
        if not path:
            return api_prefix

        return f"{api_prefix}/{path}"

    def base_url(self) -> str:
        return self._get("application", "baseurl")

    def api_url(self) -> str:
        url = self.base_url()
        port = self._get("api", "port")

        return "{}:{}{}".format(url, port, self.api_prefix())

    def database_dsn(self, context: str) -> str:
        database_config = self._config.get("database")
        host = database_config.get("host")

        database_config = database_config.get(context)

        return "mysql+pymysql://{}:{}@{}/{}?charset=utf8mb4".format(
            database_config.get("user"),
            database_config.get("password"),
            host,
            database_config.get("name"),
        )

    def mongodb_connection_settings(self) -> str:
        return self._config.get("mongodb").get("connection")

    def mongodb_databases(self):
        return self._config.get("mongodb").get("databases")

    def rabbit_connection_settings(self):
        return self._config.get("rabbitmq").get("connection")

    def rabbit_publish_exchange(self):
        exchanges = self._config.get("rabbitmq").get("exchanges")

        if not exchanges:
            return []

        return exchanges.get("publish")

    def subscribed_events(self):
        return self._subscribed_events

    def event_subscribed_commands(self, exchange: str, event: str):
        if not self._subscribed_events:
            return {}

        return self._subscribed_events.get(exchange, {}).get(event, {})

    def store_domain_even_subscriber(self) -> Dict:
        return self._config.get("application").get("store_domain_event_subscriber")

    def redis_host(self):
        return self._get("redis", "host")

    def redis_port(self):
        return self._get("redis", "port")

    def redis_database(self, database: str) -> int:
        databases = self._get("redis", "databases")

        database_number = databases.get(database)

        if not database_number:
            raise ValueError(f"{database} database does not exist")

        return database_number

    def command(self, command: str):
        return self._commands.get("commands", {}).get(command)

    def _app_root_dir(self) -> str:
        return self._get("application", "root_dir")

    def contexts(self) -> List:
        return self._contexts

    def services_files(self) -> List:
        services_dir = os.path.join(self._configs_dir(), "services/")

        return glob.glob(f"{services_dir}**/*-services.xml")

    def event_handlers_files(self) -> str:
        services_dir = os.path.join(self._configs_dir(), "services/")

        return glob.glob(f"{services_dir}**/event-handlers.xml")

    def public_key(self) -> str:
        with open(
            self._get("identity_access", "public_key_file"), encoding="utf8"
        ) as fp:
            return fp.read()

    def token_issuer(self) -> str:
        return self._get("identity_access", "token_issuer")

    def db_mapping_classes(self):
        contexts_dir = self._config.get("application").get("contexts_dir")

        context_mapping_files = {}
        mapping_modules = []
        for context in self.contexts():
            mapping_files = glob.glob(
                f"{contexts_dir}/{context}/shared/infrastructure/persistence/sqlalchemy/mapping.py"
            )

            context_mapping_files[context] = mapping_files

        for context, files in context_mapping_files.items():
            mapping_class_prefix = context.replace("_", " ").title().replace(" ", "")
            for file in files:
                module_name = file.replace(f"{contexts_dir}/", "").replace("/", ".")
                module_name = re.sub(r"\.py$", "", module_name)
                module_name = "{}.{}Mapping".format(module_name, mapping_class_prefix)
                mapping_modules.append(module_name)

        return mapping_modules

    def event_store_config_for_context(self, context: str) -> Dict:
        context_config = self._get("application", "contexts", {}).get(context)

        if not context_config:
            return {}

        return context_config.get("event_store", {})

    def is_event_store_enabled_for_context(self, context: str) -> bool:
        context_event_store = self.event_store_config_for_context(context)

        if not context_event_store:
            return False

        return context_event_store.get("enabled", False)

    def event_store_id(self, context: str) -> Optional[str]:
        context_event_store = self.event_store_config_for_context(context)

        if not context_event_store:
            return None

        return context_event_store.get("id")

    def duplicates_content_file(self, report_name: str) -> str:
        file_pattern = self._get("duplicates", "content_file")

        return file_pattern.format(self._site, report_name)

    def api_path(self):
        return "/{}".format(self.api_version())

    def logs_dir(self):
        return self._get("application", "logs_dir")

    def _configs_dir(self):
        return self._get("application", "configs_dir")

    def templates_dir(self):
        return self._get("application", "templates_dir")

    def assets_dir(self):
        return self._get("application", "assets_dir")

    def time_zone(self):
        return self._get("application", "timezone")
