"""Custom JWT authentication that enforces single-device sessions via token_version."""
from drf_spectacular.contrib.rest_framework_simplejwt import SimpleJWTScheme
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken


TOKEN_VERSION_CLAIM = "token_version"


class VersionedJWTAuthentication(JWTAuthentication):
    """Reject tokens whose token_version doesn't match the user's current value."""

    def get_user(self, validated_token):
        user = super().get_user(validated_token)
        token_version = validated_token.get(TOKEN_VERSION_CLAIM)
        if token_version != getattr(user, "token_version", 0):
            raise InvalidToken(
                {"detail": "Token is no longer valid for this device.", "code": "token_not_valid"}
            )
        return user


class VersionedJWTScheme(SimpleJWTScheme):
    target_class = "users.authentication.VersionedJWTAuthentication"
    name = "versionedJwtAuth"
