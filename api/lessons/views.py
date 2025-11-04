from http import HTTPStatus

from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from starlette.responses import Response

from lessons.models import Lesson
from lessons.permissions import IsTeacher
from lessons.serializers import LessonSerializer, AttendanceSerializer


# Create your views here.

class LessonView(APIView):
    permission_classes = [IsAuthenticated, IsTeacher]

    def get(self, request):
        lessons = Lesson.objects.filter(teacher=request.user)
        serializer = LessonSerializer(lessons, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = LessonSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save(teacher=request.user)
            return Response(serializer.data, status_code=HTTPStatus.CREATED)
        return Response(serializer.errors, HTTPStatus.BAD_REQUEST)


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


