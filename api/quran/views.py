# quran/views.py
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from quran.serializers import StudentHifzCreateSerializer
from quran.permissions import IsTeacher

class StudentHifzCreateView(APIView):
    permission_classes = [IsAuthenticated, IsTeacher]

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
