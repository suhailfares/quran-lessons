# quran/views.py
from drf_spectacular.utils import extend_schema
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from quran.serializers import StudentHifzCreateSerializer
from quran.permissions import IsTeacher

@extend_schema(tags=["Hifz"])
class StudentHifzCreateView(APIView):
    permission_classes = [IsAuthenticated, IsTeacher]

    @extend_schema(
        request=StudentHifzCreateSerializer,
        responses={
            201: StudentHifzCreateSerializer,
            400: {"type": "object"},
        },
        description="Create a new hifz entry",
        summary="Create hifz entry"
    )
    def post(self, request, *args, **kwargs):
        ser = StudentHifzCreateSerializer(data=request.data, context={"request": request})
        ser.is_valid(raise_exception=True)
        obj = ser.save()

        return Response({
            "id": obj.id,
            "student_id": obj.student_id,
            "chapter_index": obj.chapter.index,
            "start": obj.start_verse,
            "end": obj.end_verse,
            "notes": obj.notes,
            "created_at": obj.created_at,
        }, status=status.HTTP_201_CREATED)
