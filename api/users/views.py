from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.throttling import SimpleRateThrottle
from rest_framework.views import APIView

from users.models import User
from users.permissions import IsAdmin
from users.serializers import (
    PasswordChangeSerializer,
    UserCreateSerializer,
    UserReadSerializer,
    UserUpdateSerializer,
)


class RegistrationRateThrottle(SimpleRateThrottle):
    """
    Basic IP-based throttle to curb automated sign-ups.
    """
    scope = "user-registration"

    def get_cache_key(self, request, view):
        return self.get_ident(request)

    def get_rate(self):
        return "5/hour"


@extend_schema(
    tags=["Users"],
    summary="Register a teacher account",
    description="Creates a new teacher record and returns a sanitized representation."
)
class UserCreateView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer
    permission_classes = [permissions.AllowAny]
    throttle_classes = [RegistrationRateThrottle]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        read_serializer = UserReadSerializer(user, context={"request": request})
        headers = self.get_success_headers(read_serializer.data)
        return Response(read_serializer.data, status=status.HTTP_201_CREATED, headers=headers)


@extend_schema(tags=["Users"])
class CurrentUserView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="Get the authenticated user's profile",
        responses={200: UserReadSerializer},
    )
    def get(self, request):
        return Response(UserReadSerializer(request.user).data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Update the authenticated user's profile",
        request=UserUpdateSerializer,
        responses={200: UserReadSerializer},
    )
    def patch(self, request):
        serializer = UserUpdateSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(UserReadSerializer(request.user).data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Replace the authenticated user's profile fields",
        request=UserUpdateSerializer,
        responses={200: UserReadSerializer},
    )
    def put(self, request):
        serializer = UserUpdateSerializer(request.user, data=request.data, partial=False)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(UserReadSerializer(request.user).data, status=status.HTTP_200_OK)


@extend_schema(
    tags=["Users"],
    summary="List all users",
    description="Returns all registered users. Admins only. Pass `mosque_name` to filter by mosque.",
    parameters=[
        OpenApiParameter(
            name="mosque_name",
            description="Filter users by mosque name (case-insensitive contains).",
            required=False,
            type=str,
        )
    ],
    responses={200: UserReadSerializer(many=True)},
)
class UserListView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdmin]

    def get(self, request):
        qs = User.objects.all()
        mosque_name = request.query_params.get("mosque_name")
        if mosque_name:
            qs = qs.filter(mosque_name__icontains=mosque_name)
        return Response(UserReadSerializer(qs, many=True).data, status=status.HTTP_200_OK)


@extend_schema(
    tags=["Users"],
    summary="Delete a user by username",
    description="Permanently deletes the user with the given username. Admins only.",
    responses={204: None},
)
class UserDeleteView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdmin]

    def delete(self, request, username):
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(
    tags=["Users"],
    summary="Change the authenticated user's password",
    description="Requires the current password. All existing sessions are invalidated on success.",
    request=PasswordChangeSerializer,
    responses={204: None},
)
class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = PasswordChangeSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        user = request.user
        user.set_password(serializer.validated_data["new_password"])
        user.token_version = (user.token_version or 0) + 1
        user.save(update_fields=["password", "token_version"])

        return Response(status=status.HTTP_204_NO_CONTENT)
