from http import HTTPStatus

from django.db import transaction
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.response import Response

from lessons.models import Lesson, Attendance
from lessons.permissions import IsTeacher
from lessons.serializers import (
    LessonSerializer,
    AttendanceSerializer,
    BulkAttendancePayloadSerializer,
    AttendanceListResponseSerializer,
)
from students.models import Student
from students.serializers import StudentSerializer


# Create your views here.


@extend_schema(
    tags=["Lessons"],
    summary="List and create lessons",
    description="GET returns lessons for the logged-in teacher. POST creates a lesson for that teacher."
)
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

    def _get_lesson(self, lesson_id, user):
        try:
            lesson = Lesson.objects.get(id=lesson_id)
        except Lesson.DoesNotExist:
            return None, Response(
                {"detail": "Lesson not found"},
                status=HTTPStatus.NOT_FOUND,
            )

        if lesson.teacher_id != user.id:
            return None, Response(
                {"detail": "You can only mark attendances for your own lessons"},
                status=HTTPStatus.FORBIDDEN,
            )

        return lesson, None

    @extend_schema(
        summary="Bulk mark attendance",
        description="Accepts lesson_id and array of students (each with studentId) and marks them attended=True.",
        request=BulkAttendancePayloadSerializer,
        responses={
            201: AttendanceSerializer(many=True),
            400: {"type": "object"},
            403: {"type": "object"},
            404: {"type": "object"},
        },
    )
    def post(self, request, lesson_id=None):
        if not isinstance(request.data, dict):
            return Response(
                {"detail": "Expected an object with lesson_id and students."},
                status=HTTPStatus.BAD_REQUEST,
            )

        payload_serializer = BulkAttendancePayloadSerializer(
            data=request.data,
            context={"lesson_id": lesson_id},
        )
        payload_serializer.is_valid(raise_exception=True)
        lesson_id = payload_serializer.validated_data["lesson_id"]

        lesson, error_response = self._get_lesson(lesson_id, request.user)
        if error_response:
            return error_response

        student_ids = [
            entry["studentId"] for entry in payload_serializer.validated_data["students"]
        ]
        unique_ids = set(student_ids)

        students = Student.objects.filter(id__in=unique_ids, teacher=request.user)
        student_map = {student.id: student for student in students}
        missing_ids = sorted(unique_ids - set(student_map.keys()))

        if missing_ids:
            return Response(
                {"detail": f"Students not found or not assigned to you: {missing_ids}"},
                status=HTTPStatus.BAD_REQUEST,
            )

        attendances = []
        with transaction.atomic():
            for entry in payload_serializer.validated_data["students"]:
                student = student_map[entry["studentId"]]
                attendance, _ = Attendance.objects.update_or_create(
                    student=student,
                    lesson=lesson,
                    defaults={"attended": True},
                )
                attendances.append(attendance)

        response_data = AttendanceSerializer(attendances, many=True).data
        return Response(response_data, status=HTTPStatus.CREATED)

    @extend_schema(
        summary="List attendance roster",
        description="Returns lesson_id and the list of students (per Student model) marked for this lesson.",
        parameters=[
            OpenApiParameter(
                name="lesson_id",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=False,
                description="Lesson identifier (omit when using /lessons/{lesson_id}/attendances).",
            )
        ],
        responses={
            200: AttendanceListResponseSerializer,
            403: {"type": "object"},
            404: {"type": "object"},
        },
    )
    def get(self, request, lesson_id=None):
        if lesson_id is None:
            lesson_id_param = request.query_params.get("lesson_id")
            if lesson_id_param is None:
                return Response(
                    {"detail": "Provide lesson_id in the URL or as a query parameter."},
                    status=HTTPStatus.BAD_REQUEST,
                )
            try:
                lesson_id = int(lesson_id_param)
            except ValueError:
                return Response(
                    {"detail": "lesson_id must be an integer."},
                    status=HTTPStatus.BAD_REQUEST,
                )

        lesson, error_response = self._get_lesson(lesson_id, request.user)
        if error_response:
            return error_response

        attendances = (
            Attendance.objects.filter(lesson=lesson)
            .select_related("student")
            .order_by("student__first_name", "student__last_name")
        )
        students = [attendance.student for attendance in attendances]
        students_data = StudentSerializer(students, many=True).data
        response_payload = {
            "lesson_id": lesson.id,
            "students": students_data,
        }
        return Response(response_payload, status=HTTPStatus.OK)
