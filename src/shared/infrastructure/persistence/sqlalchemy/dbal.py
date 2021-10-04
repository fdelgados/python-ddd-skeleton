from sqlalchemy import create_engine, text, exc

import shared.infrastructure.environment.globalvars as glob
from shared.domain.service.persistence.dbal import DbalService, DbalServiceError


class SqlAlchemyDbalService(DbalService):
    def __init__(self, context: str):
        dsn = glob.settings.database_dsn(context)
        self._connection = create_engine(dsn)

    def execute(self, sentence: str, **parameters):
        with self._connection.connect() as connection:
            try:
                return connection.execute(text(sentence), **parameters)
            except exc.SQLAlchemyError as error:
                raise DbalServiceError(str(error))
            finally:
                connection.close()
