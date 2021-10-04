import threading
from typing import List, Dict
from contextlib import contextmanager
from sqlalchemy import create_engine, desc, asc
from sqlalchemy.orm import sessionmaker, scoped_session

from shared.domain.model.aggregate import AggregateRoot
from shared.domain.model.repository import Repository as BaseRepository


class ScopedSessionError(RuntimeError):
    pass


class SessionBuilder:
    _session = None
    _lock = threading.Lock()

    @classmethod
    def build(cls, dsn: str) -> scoped_session:
        if not cls._session:
            with cls._lock:
                if not cls._session:
                    session_factory = sessionmaker(
                        bind=create_engine(dsn), expire_on_commit=False
                    )
                    cls._session = scoped_session(session_factory)

        return cls._session


@contextmanager
def session_scope(dsn: str):
    Session = SessionBuilder.build(dsn)
    session = Session()

    try:
        yield session
    except Exception as error:
        raise ScopedSessionError(str(error))
    finally:
        session.close()
        Session.remove()


class Repository(BaseRepository):
    def __init__(self, aggregate: AggregateRoot, dsn: str):
        self._aggregate = aggregate
        self._dsn = dsn

    def create_connection(self):
        return create_engine(self._dsn)

    def add(self, aggregate: AggregateRoot) -> None:
        with session_scope(self._dsn) as session:
            session.add(aggregate)
            session.commit()

    def save(self, aggregate: AggregateRoot) -> None:
        with session_scope(self._dsn) as session:
            session.add(aggregate)
            session.commit()

    def find(self, **kwargs) -> AggregateRoot:
        with session_scope(self._dsn) as session:
            result = session.query(self._aggregate).filter_by(**kwargs).first()

        return result

    def find_all(self, order_by: Dict = None, **kwargs) -> List[AggregateRoot]:
        with session_scope(self._dsn) as session:
            query = session.query(self._aggregate).filter_by(**kwargs)
            if order_by:
                for field, direction in order_by.items():
                    if direction == "desc":
                        order_expression = desc(self._aggregate.__dict__[field])
                    else:
                        order_expression = asc(self._aggregate.__dict__[field])

                    query = query.order_by(order_expression)

            results = query.all()

        return results
