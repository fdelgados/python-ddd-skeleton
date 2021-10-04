class User:
    def __init__(self, tenant_id: str, username: str, email: str):
        self._tenant_id = tenant_id
        self._username = username
        self._email = email

    def tenant_id(self) -> str:
        return self._tenant_id

    def username(self) -> str:
        return self._username

    def email(self) -> str:
        return self._email
