from drf_spectacular.utils import extend_schema
from rest_framework import generics, permissions

from users.models import User
from users.serializers import UserCreateSerializer

@extend_schema(tags=["Users"])
class UserCreateView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer
    permission_classes = [permissions.AllowAny]