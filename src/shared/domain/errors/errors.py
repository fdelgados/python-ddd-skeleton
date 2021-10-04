from shared.domain.model.valueobject.error import Error


class Errors:
    @staticmethod
    def generic():
        return Error(1000, "Application error")

    @staticmethod
    def missing_request_parameter():
        return Error(1001, "Your request is missing parameters")

    @staticmethod
    def invalid_request_parameter():
        return Error(1002, "Your request contains invalid parameters")

    @staticmethod
    def authorization(**kwargs):
        details = kwargs.get("details")
        return Error(2001, "Authorization failed", details)

    @staticmethod
    def access_token_expired():
        return Error(
            2002,
            "Access token has expired. You can use the refresh token to obtain a new one",
        )

    @staticmethod
    def missing_access_token():
        return Error(2003, "Access token not provided")

    @staticmethod
    def entity_not_found(**kwargs):
        code = 3001
        if kwargs.get("message"):
            return Error(code, kwargs.get("message"))

        entity_name = kwargs.get("entity_name")
        entity_id = kwargs.get("entity_id")

        if entity_name and entity_id:
            return Error(code, f"{entity_name} identified by <{entity_id}> not found")

        if entity_name:
            return Error(code, f"{entity_name} not found")

        return Error(code, "Entity not found")

    @staticmethod
    def conflict_error(**kwargs) -> Error:
        code = 3001
        if kwargs.get("message"):
            return Error(code, f'Conflict. {kwargs.get("message")}.')

        return Error(code, 'Conflict.')


class ApplicationError(RuntimeError):
    def __init__(self, error: Error) -> None:
        self.error = error
        self.message = error.message
        self.code = error.code

    def __str__(self):
        return self.message
