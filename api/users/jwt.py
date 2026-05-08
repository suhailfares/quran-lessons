"""Login/refresh views that stamp tokens with the user's current token_version."""
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from users.authentication import TOKEN_VERSION_CLAIM
from users.models import User


def _attach_version(token, version):
    token[TOKEN_VERSION_CLAIM] = version


class VersionedTokenObtainPairSerializer(TokenObtainPairSerializer):
    """On login, bump the user's token_version and stamp the new tokens with it."""

    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user
        user.token_version = (user.token_version or 0) + 1
        user.save(update_fields=["token_version"])

        refresh = RefreshToken(data["refresh"])
        _attach_version(refresh, user.token_version)
        access = refresh.access_token
        _attach_version(access, user.token_version)

        data["refresh"] = str(refresh)
        data["access"] = str(access)
        return data


class VersionedTokenObtainPairView(TokenObtainPairView):
    serializer_class = VersionedTokenObtainPairSerializer


class VersionedTokenRefreshView(TokenRefreshView):
    """On refresh, the incoming refresh token's token_version must match the user's current value."""

    def post(self, request, *args, **kwargs):
        raw = request.data.get("refresh")
        if raw:
            try:
                token = RefreshToken(raw)
            except Exception:
                # Let the parent view produce its standard error response.
                return super().post(request, *args, **kwargs)

            user_id = token.get("user_id")
            claim_version = token.get(TOKEN_VERSION_CLAIM)
            user = User.objects.filter(pk=user_id).only("token_version").first()
            if user is None or claim_version != user.token_version:
                raise InvalidToken(
                    {"detail": "Token is no longer valid for this device.", "code": "token_not_valid"}
                )

        response = super().post(request, *args, **kwargs)

        if response.status_code == 200 and "access" in response.data:
            access = AccessToken(response.data["access"])
            user_id = access.get("user_id")
            user = User.objects.filter(pk=user_id).only("token_version").first()
            if user is not None:
                _attach_version(access, user.token_version)
                response.data["access"] = str(access)
        return response
