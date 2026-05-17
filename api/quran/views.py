# quran/views.py
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from quran.models import StudentHifz, QuranSabr
from quran.permissions import IsTeacher
from quran.serializers import (
    StudentHifzCreateSerializer,
    StudentHifzSerializer,
    StudentHifzUpdateSerializer,
    QuranSabrCreateSerializer,
    QuranSabrSerializer,
)
from quranlessons.sync import apply_sync_filter


SYNC_PARAM = OpenApiParameter(
    name="updated_since",
    type=OpenApiTypes.DATETIME,
    location=OpenApiParameter.QUERY,
    required=False,
    description="ISO-8601 UTC. Returns only rows updated_at > updated_since (and includes tombstones).",
)


def _serialize(obj: StudentHifz):
    return StudentHifzSerializer(obj).data


@extend_schema(tags=["Hifz"])
class StudentHifzListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsTeacher]

    @extend_schema(
        responses={200: StudentHifzSerializer(many=True)},
        description="List hifz entries for the authenticated teacher's students.",
        summary="List hifz entries",
        parameters=[SYNC_PARAM],
    )
    def get(self, request, *args, **kwargs):
        queryset = (
            StudentHifz.objects.filter(student__teacher=request.user)
            .select_related("chapter", "student")
            .order_by("-created_at")
        )
        queryset = apply_sync_filter(queryset, request)
        data = [_serialize(obj) for obj in queryset]
        return Response(data, status=status.HTTP_200_OK)

    @extend_schema(
        request=StudentHifzCreateSerializer,
        responses={201: StudentHifzSerializer, 400: {"type": "object"}},
        description="Create a new hifz entry",
        summary="Create hifz entry",
    )
    def post(self, request, *args, **kwargs):
        ser = StudentHifzCreateSerializer(data=request.data, context={"request": request})
        ser.is_valid(raise_exception=True)
        obj = ser.save()
        return Response(_serialize(obj), status=status.HTTP_201_CREATED)


@extend_schema(tags=["Hifz"], responses={200: StudentHifzSerializer})
class StudentHifzDetailView(APIView):
    permission_classes = [IsAuthenticated, IsTeacher]
    serializer_class = StudentHifzSerializer

    def _get_object(self, request, pk):
        try:
            obj = StudentHifz.objects.select_related("chapter", "student").get(pk=pk)
        except StudentHifz.DoesNotExist:
            return None, Response({"detail": "Hifz entry not found."}, status=status.HTTP_404_NOT_FOUND)
        if obj.student.teacher_id != request.user.id:
            return None, Response({"detail": "Not yours."}, status=status.HTTP_403_FORBIDDEN)
        return obj, None

    @extend_schema(responses={200: StudentHifzSerializer})
    def get(self, request, pk):
        obj, err = self._get_object(request, pk)
        if err:
            return err
        return Response(_serialize(obj), status=status.HTTP_200_OK)

    @extend_schema(request=StudentHifzUpdateSerializer, responses={200: StudentHifzSerializer})
    def put(self, request, pk):
        return self._update(request, pk, partial=False)

    @extend_schema(request=StudentHifzUpdateSerializer, responses={200: StudentHifzSerializer})
    def patch(self, request, pk):
        return self._update(request, pk, partial=True)

    def _update(self, request, pk, partial):
        obj, err = self._get_object(request, pk)
        if err:
            return err
        ser = StudentHifzUpdateSerializer(obj, data=request.data, partial=partial)
        ser.is_valid(raise_exception=True)
        ser.update(obj, ser.validated_data)
        return Response(_serialize(obj), status=status.HTTP_200_OK)

    def delete(self, request, pk):
        obj, err = self._get_object(request, pk)
        if err:
            return err
        if not obj.is_deleted:
            obj.is_deleted = True
            obj.save(update_fields=["is_deleted", "updated_at"])
        return Response(status=status.HTTP_204_NO_CONTENT)


def _serialize_quran_sabr(obj: QuranSabr):
    return QuranSabrSerializer(obj).data


@extend_schema(tags=["Sabr"])
class QuranSabrListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsTeacher]

    @extend_schema(
        responses={200: QuranSabrSerializer(many=True)},
        description="List quran sabr entries for the authenticated teacher's students.",
        summary="List quran sabr entries",
        parameters=[SYNC_PARAM],
    )
    def get(self, request, *args, **kwargs):
        queryset = (
            QuranSabr.objects.filter(student__teacher=request.user)
            .select_related("student")
            .order_by("-created_at")
        )
        queryset = apply_sync_filter(queryset, request)
        data = [_serialize_quran_sabr(obj) for obj in queryset]
        return Response(data, status=status.HTTP_200_OK)

    @extend_schema(
        request=QuranSabrCreateSerializer,
        responses={201: QuranSabrSerializer, 400: {"type": "object"}},
        description="Create a new quran sabr entry",
        summary="Create quran sabr entry",
    )
    def post(self, request, *args, **kwargs):
        ser = QuranSabrCreateSerializer(data=request.data, context={"request": request})
        ser.is_valid(raise_exception=True)
        obj = ser.save()
        return Response(_serialize_quran_sabr(obj), status=status.HTTP_201_CREATED)


