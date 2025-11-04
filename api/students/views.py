from django.shortcuts import render

# Create your views here.

from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied

from .models import Student
from rest_framework import permissions

from .permissions import IsTeacher
from .serializers import StudentSerializer

"""
class IsTeacher(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "teacher"
"""

class StudentViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, IsTeacher]
    serializer_class = StudentSerializer

    def get_queryset(self):
        return Student.objects.filter(teacher=self.request.user)


    def perform_create(self, serializer):
        serializer.save(teacher=self.request.user)

    def perform_update(self, serializer):
        student = self.get_object()
        if student.teacher != self.request.user:
            raise PermissionDenied("You can only edit your own students.")
        serializer.save()

    def perform_destroy(self, instance):
        if instance.teacher != self.request.user:
            PermissionDenied("You can only delete your own student")
        instance.delete()

    """
    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return StudentReadSerializer
        return StudentWriteSerializer
    """
