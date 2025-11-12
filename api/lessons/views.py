from http import HTTPStatus

from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework import generics
from starlette.responses import Response

from lessons.models import Lesson
from lessons.permissions import IsTeacher
from lessons.serializers import LessonSerializer, AttendanceSerializer


# Create your views here.


@extend_schema(tags=["Lessons"])
class LessonView(generics.ListCreateAPIView):
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, IsTeacher]

    def get_queryset(self):
        return Lesson.objects.filter(teacher=self.request.user)

    def perform_create(self, serializer):
        serializer.save(teacher=self.request.user)

@extend_schema(tags=["Attendances"])
class AttendanceView(APIView):
    permission_classes = [IsAuthenticated, IsTeacher]

    def post(self, request):
        user = request.user
        serializer = AttendanceSerializer(data = request.data)

        if serializer.is_valid():
            lesson = serializer.validated_data["lesson"]
            student = serializer.validated_data["user"]

            if lesson.teacher != user:
                return Response(
                    {"detail": "You can only mark attendances for your own lessons"},
                    status_code=HTTPStatus.FORBIDDEN
                )

            if student.teacher != user:
                return Response(
                    {"detail": "You can only mark attendances for you own students"}
                )

            serializer.save()
            return Response(serializer.data, status_code=HTTPStatus.CREATED)

        return Response(serializer.errors, status_code=HTTPStatus.BAD_REQUEST)


