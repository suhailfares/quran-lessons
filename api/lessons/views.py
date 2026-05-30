from datetime import date as date_cls
from http import HTTPStatus

from django.db import transaction
from django.utils import timezone
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from lessons.models import Lesson, Attendance
from lessons.permissions import IsTeacher
from lessons.serializers import (
    LessonSerializer,
    AttendanceSerializer,
    BulkAttendancePayloadSerializer,
    AttendanceListResponseSerializer,
)
from quranlessons.roles import is_admin, resolve_create_teacher
from quranlessons.sync import SoftDeleteDestroyMixin, apply_sync_filter
from students.models import Student
from students.serializers import StudentSerializer


SYNC_PARAM = OpenApiParameter(
    name="updated_since",
    type=OpenApiTypes.DATETIME,
    location=OpenApiParameter.QUERY,
    required=False,
    description="ISO-8601 UTC. Returns only rows updated_at > updated_since (and includes tombstones).",
)


@extend_schema(
    tags=["Lessons"],
    parameters=[SYNC_PARAM],
)
@extend_schema_view(
    create=extend_schema(
        description=(
            "Admins may include `teacher` (a teacher's user id) in the body to assign the "
            "new record to that teacher; non-admins always own what they create."
        ),
    ),
)
class LessonViewSet(SoftDeleteDestroyMixin, viewsets.ModelViewSet):
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, IsTeacher]
    queryset = Lesson.objects.all()

    def get_queryset(self):
        user = self.request.user
        qs = Lesson.objects.all() if is_admin(user) else Lesson.objects.filter(teacher=user)
        return apply_sync_filter(qs, self.request)

    def perform_create(self, serializer):
        serializer.save(teacher=resolve_create_teacher(self.request, serializer))


def _parse_date_param(raw):
    if raw is None:
        return None
    try:
        return date_cls.fromisoformat(raw)
    except ValueError:
        return ...


@extend_schema(tags=["Attendances"])
class AttendanceView(APIView):
    permission_classes = [IsAuthenticated, IsTeacher]

    def _get_lesson(self, lesson_id, user):
        try:
            lesson = Lesson.objects.get(id=lesson_id)
        except Lesson.DoesNotExist:
            return None, Response(
                {"detail": "Lesson not found"}, status=HTTPStatus.NOT_FOUND,
            )
        if not is_admin(user) and lesson.teacher_id != user.id:
            return None, Response(
                {"detail": "You can only mark attendances for your own lessons"},
                status=HTTPStatus.FORBIDDEN,
            )
        return lesson, None

    @extend_schema(
        summary="Bulk mark attendance for a lesson on a date",
        description=(
            "Upserts attendance for each (lesson, student, date). Students in the payload "
            "are set to attended=true; students for that lesson+date NOT in the payload "
            "are set to attended=false (payload is the source of truth for the day)."
        ),
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
                {"detail": "Expected an object with lesson_id, date, and students."},
                status=HTTPStatus.BAD_REQUEST,
            )

        payload_serializer = BulkAttendancePayloadSerializer(
            data=request.data,
            context={"lesson_id": lesson_id},
        )
        payload_serializer.is_valid(raise_exception=True)
        lesson_id = payload_serializer.validated_data["lesson_id"]
        attendance_date = payload_serializer.validated_data["date"]

        lesson, error_response = self._get_lesson(lesson_id, request.user)
        if error_response:
            return error_response

        student_ids = [
            entry["studentId"] for entry in payload_serializer.validated_data["students"]
        ]
        unique_ids = set(student_ids)

        students = Student.objects.filter(id__in=unique_ids)
        if not is_admin(request.user):
            students = students.filter(teacher=request.user)
        student_map = {student.id: student for student in students}
        missing_ids = sorted(unique_ids - set(student_map.keys()))
        if missing_ids:
            return Response(
                {"detail": f"Students not found or not assigned to you: {missing_ids}"},
                status=HTTPStatus.BAD_REQUEST,
            )

        attendances = []
        with transaction.atomic():
            # mark not-listed students for the day as absent
            Attendance.objects.filter(
                lesson=lesson, date=attendance_date,
            ).exclude(student_id__in=unique_ids).update(
                attended=False, is_deleted=False, updated_at=timezone.now(),
            )

            for student in (student_map[sid] for sid in unique_ids):
                attendance, _ = Attendance.objects.update_or_create(
                    student=student,
                    lesson=lesson,
                    date=attendance_date,
                    defaults={"attended": True, "is_deleted": False},
                )
                attendances.append(attendance)

        response_data = AttendanceSerializer(attendances, many=True).data
        return Response(response_data, status=HTTPStatus.CREATED)

    @extend_schema(
        summary="List attendance roster for a lesson on a date",
        parameters=[
            OpenApiParameter(
                name="lesson_id", type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY, required=False,
                description="Lesson identifier (omit when using /lessons/{lesson_id}/attendances).",
            ),
            OpenApiParameter(
                name="date", type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY, required=False,
                description="Day to query. Defaults to today (UTC).",
            ),
            SYNC_PARAM,
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

        date_raw = request.query_params.get("date")
        parsed = _parse_date_param(date_raw)
        if parsed is ...:
            return Response(
                {"detail": "date must be YYYY-MM-DD."},
                status=HTTPStatus.BAD_REQUEST,
            )
        attendance_date = parsed or timezone.now().date()

        lesson, error_response = self._get_lesson(lesson_id, request.user)
        if error_response:
            return error_response

        attendances = (
            Attendance.objects.filter(lesson=lesson, date=attendance_date)
            .select_related("student")
            .order_by("student__first_name", "student__last_name")
        )
        attendances = apply_sync_filter(attendances, request)
        students = [a.student for a in attendances]
        students_data = StudentSerializer(students, many=True).data
        return Response(
            {"lesson_id": lesson.id, "date": attendance_date, "students": students_data},
            status=HTTPStatus.OK,
        )
