from functools import wraps
from flask import request
import credential_shield as cs

from shared.domain.model.entity.user import User
from shared.domain.errors.errors import Errors, ApplicationError

import shared.infrastructure.environment.globalvars as glob


def authorization_required(scope: str):
    def decorator(func):
        @wraps(func)
        def decorated_function(self, *args, **kwargs):
            auth_header = request.headers.get("Authorization")
            if not auth_header:
                raise ApplicationError(Errors.missing_access_token())

            token_validator = cs.TokenValidator(
                glob.settings.application_id(), scope, glob.settings.token_issuer()
            )

            try:
                token: cs.Token = token_validator.validate(
                    auth_header, glob.settings.public_key()
                )
                user = User(token.tenant_id(), token.username(), token.user_email())
                kwargs["user"] = user

                return func(self, *args, **kwargs)
            except cs.ExpiredTokenException:
                raise ApplicationError(Errors.access_token_expired())
            except cs.CredentialShieldException as error:
                raise ApplicationError(Errors.authorization(details=str(error)))

        return decorated_function

    return decorator
