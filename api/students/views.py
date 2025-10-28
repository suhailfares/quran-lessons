from django.shortcuts import render

# Create your views here.

from rest_framework import viewsets
from .models import Student
from rest_framework import permissions
from .serializers import StudentReadSerializer, StudentWriteSerializer

class IsTeacher(permissions.BasePermission):
    """
       Custom permission to allow only teachers to create/manage students.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "teacher"

class StudentViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, IsTeacher]

    def get_queryset(self):
        return Student.objects.filter(teacher=self.request.user)

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return StudentReadSerializer
        return StudentWriteSerializer

    def perform_create(self, serializer):
        serializer.save(teacher=self.request.user)