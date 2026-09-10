from dataclasses import dataclass

from django.core import signing
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.authentication import JWTAuthentication


CODE_ADMIN_TOKEN_PREFIX = "code-admin."
CODE_ADMIN_TOKEN_SALT = "admin-api-code-login"
CODE_ADMIN_TOKEN_MAX_AGE = 60 * 60 * 2


@dataclass
class CodeAdminUser:
    username: str
    email: str

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_superuser(self):
        return True

    @property
    def is_staff(self):
        return True

    @property
    def pk(self):
        return None


class AdminAuthentication(BaseAuthentication):
    """Accept the code-admin token, while retaining normal JWT logins."""

    def authenticate(self, request):
        authorization = request.headers.get("Authorization", "")
        if not authorization.startswith("Bearer "):
            return None

        token = authorization[7:]
        if token.startswith(CODE_ADMIN_TOKEN_PREFIX):
            try:
                payload = signing.loads(
                    token[len(CODE_ADMIN_TOKEN_PREFIX) :],
                    salt=CODE_ADMIN_TOKEN_SALT,
                    max_age=CODE_ADMIN_TOKEN_MAX_AGE,
                )
            except signing.BadSignature as error:
                raise AuthenticationFailed("Invalid or expired administrator session.") from error
            return CodeAdminUser(payload["username"], payload["email"]), token

        return JWTAuthentication().authenticate(request)

    def authenticate_header(self, request):
        return "Bearer"
