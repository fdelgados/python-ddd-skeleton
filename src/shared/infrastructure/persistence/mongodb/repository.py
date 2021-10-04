import abc

from typing import List, Optional

from pymongo import MongoClient

from shared.domain.model.aggregate import AggregateRoot
from shared.domain.model.repository import Repository
import shared.infrastructure.environment.globalvars as glob


class MongoDbRepository(Repository, metaclass=abc.ABCMeta):
    def __init__(self, database: str):
        databases = glob.settings.mongodb_databases()
        connection_settings = glob.settings.mongodb_connection_settings()

        self._database = databases.get(database)
        self._client = MongoClient(
            connection_settings.get("host"),
            port=connection_settings.get("port"),
            username=connection_settings.get("username"),
            password=connection_settings.get("password"),
            authSource=self._database,
            connect=False,
        )

    @property
    def client(self) -> MongoClient:
        return self._client

    @property
    def database(self):
        return self.client[self._database]

    def add(self, aggregate: AggregateRoot) -> None:
        pass

    def save(self, aggregate: AggregateRoot) -> None:
        pass

    def find(self, **kwargs) -> Optional[AggregateRoot]:
        pass

    def find_all(self, **kwargs) -> List[AggregateRoot]:
        pass
