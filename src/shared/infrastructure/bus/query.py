from typing import Optional
from shared.utils import camel_to_snake_case, class_fullname
from shared.domain.bus.query import (
    Query,
    QueryHandler,
    QueryBus,
    Response,
    QueryNotRegisteredError,
    QueryNotCallableError,
)
import shared.infrastructure.environment.globalvars as glob


class QueryBusImpl(QueryBus):
    def ask(self, query: Query) -> Optional[Response]:

        query_fullname = class_fullname(query)
        module, query_name = query_fullname.rsplit(".", maxsplit=1)

        handler_id = "{}.{}_handler".format(module, camel_to_snake_case(query_name))

        query_handler: QueryHandler = glob.container.get(handler_id)

        if not query_handler:
            raise QueryNotRegisteredError(query)

        if not isinstance(query_handler, QueryHandler):
            raise QueryNotRegisteredError(query)

        if not hasattr(query_handler, "handle") or not callable(query_handler.handle):
            raise QueryNotCallableError(query)

        return query_handler.handle(query)
