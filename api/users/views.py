from drf_spectacular.utils import extend_schema
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.throttling import SimpleRateThrottle
from rest_framework.views import APIView

from users.models import User
from users.serializers import UserCreateSerializer, UserReadSerializer, UserUpdateSerializer


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
