from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import User
from quranlessons.roles import is_strict_admin, is_manager
from users.permissions import IsAdmin, IsStrictAdmin
from users.serializers import (
    AdminCreateSerializer,
    ManagerCreateSerializer,
    PasswordChangeSerializer,
    UserCreateSerializer,
    UserReadSerializer,
    UserUpdateSerializer,
)


@extend_schema(
    tags=["Users"],
    summary="Register a teacher account",
    description="Creates a new teacher record and returns a sanitized representation. Admins only."
)
class UserCreateView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]

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
        user = request.user
        if is_strict_admin(user):
            qs = User.objects.all()
            mosque_name = request.query_params.get("mosque_name")
            if mosque_name:
                qs = qs.filter(mosque_name__icontains=mosque_name)
        elif is_manager(user):
            qs = User.objects.filter(mosque_name=user.mosque_name, role="teacher")
        else:
            qs = User.objects.none()
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
        requester = request.user
        if getattr(user, "role", None) == "admin" and not is_strict_admin(requester):
            return Response({"detail": "Only admins can delete admin accounts."}, status=status.HTTP_403_FORBIDDEN)
        if is_manager(requester):
            if getattr(user, "mosque_name", None) != requester.mosque_name:
                return Response({"detail": "You can only delete users in your mosque."}, status=status.HTTP_403_FORBIDDEN)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(
    tags=["Users"],
    summary="Create an admin account",
    description="Creates a new user with role=admin. Strict admins only (managers cannot create admins).",
    request=AdminCreateSerializer,
    responses={201: UserReadSerializer},
)
class AdminCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsStrictAdmin]

    def post(self, request):
        serializer = AdminCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(UserReadSerializer(user).data, status=status.HTTP_201_CREATED)


@extend_schema(
    tags=["Users"],
    summary="Create a manager account",
    description="Creates a new user with role=manager. Admins only.",
    request=ManagerCreateSerializer,
    responses={201: UserReadSerializer},
)
class ManagerCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdmin]

    def post(self, request):
        serializer = ManagerCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(UserReadSerializer(user).data, status=status.HTTP_201_CREATED)


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
