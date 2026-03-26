# quran/views.py
from drf_spectacular.utils import extend_schema
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from quran.models import StudentHifz
from quran.serializers import StudentHifzCreateSerializer, StudentHifzSerializer
from quran.permissions import IsTeacher

@extend_schema(tags=["Hifz"])
class StudentHifzCreateView(APIView):
    permission_classes = [IsAuthenticated, IsTeacher]

    def _serialize(self, obj: StudentHifz):
        return {
            "id": obj.id,
            "student_id": obj.student_id,
            "chapter_index": obj.chapter.index,
            "start": obj.start_verse,
            "end": obj.end_verse,
            "notes": obj.notes,
            "date": obj.created_at,
        }

    @extend_schema(
        responses={200: StudentHifzSerializer(many=True)},
        description="List hifz entries for the authenticated teacher's students.",
        summary="List hifz entries",
    )
    def get(self, request, *args, **kwargs):
        queryset = (
            StudentHifz.objects.filter(student__teacher=request.user)
            .select_related("chapter", "student")
            .order_by("-created_at")
        )
        data = [self._serialize(obj) for obj in queryset]
        return Response(data, status=status.HTTP_200_OK)

    @extend_schema(
        request=StudentHifzCreateSerializer,
        responses={
            201: StudentHifzSerializer,
            400: {"type": "object"},
        },
        description="Create a new hifz entry",
        summary="Create hifz entry"
    )
    def post(self, request, *args, **kwargs):
        ser = StudentHifzCreateSerializer(data=request.data, context={"request": request})
        ser.is_valid(raise_exception=True)
        obj = ser.save()

        return Response(self._serialize(obj), status=status.HTTP_201_CREATED)
