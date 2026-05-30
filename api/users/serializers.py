from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from .models import User


class PasswordChangeSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)

    def validate_current_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Current password is incorrect.")
        return value

    def validate_new_password(self, value):
        validate_password(value, user=self.context["request"].user)
        return value


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "first_name",
            "last_name",
            "phone_number",
            "mosque_name",
            "study",
            "date_of_birth",
            "certificates",
            "password",  # input only
        ]
        read_only_fields = []

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(role="teacher", **validated_data)
        user.set_password(password)  # ✅ hash password
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        validated_data.pop("role", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class AdminCreateSerializer(UserCreateSerializer):
    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(role="admin", **validated_data)
        user.set_password(password)
        user.save()
        return user


class ManagerCreateSerializer(UserCreateSerializer):
    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(role="manager", **validated_data)
        user.set_password(password)
        user.save()
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "email",
            "first_name",
            "last_name",
            "phone_number",
            "study",
            "date_of_birth",
            "certificates",
        ]


class UserReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "phone_number",
            "mosque_name",
            "study",
            "date_of_birth",
            "certificates",
            "role",
        ]
