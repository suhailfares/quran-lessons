from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from hadith.models import HadithSabr, HadithHifz
from hadith.permissions import IsTeacher
from hadith.serializers import (
    HadithSabrCreateSerializer,
    HadithSabrSerializer,
    HadithHifzCreateSerializer,
    HadithHifzUpdateSerializer,
    HadithHifzSerializer,
)
from quranlessons.sync import apply_sync_filter


SYNC_PARAM = OpenApiParameter(
    name="updated_since",
    type=OpenApiTypes.DATETIME,
    location=OpenApiParameter.QUERY,
    required=False,
    description="ISO-8601 UTC. Returns only rows updated_at > updated_since (and includes tombstones).",
)


def _serialize_hadith_sabr(obj: HadithSabr):
    return HadithSabrSerializer(obj).data


def _serialize_hadith_hifz(obj: HadithHifz):
    return HadithHifzSerializer(obj).data


@extend_schema(tags=["Sabr"])
class HadithSabrListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsTeacher]

    @extend_schema(
        responses={200: HadithSabrSerializer(many=True)},
        description="List hadith sabr entries for the authenticated teacher's students.",
        summary="List hadith sabr entries",
        parameters=[SYNC_PARAM],
    )
    def get(self, request, *args, **kwargs):
        queryset = (
            HadithSabr.objects.filter(student__teacher=request.user)
            .select_related("student")
            .order_by("-created_at")
        )
        queryset = apply_sync_filter(queryset, request)
        data = [_serialize_hadith_sabr(obj) for obj in queryset]
        return Response(data, status=status.HTTP_200_OK)

    @extend_schema(
        request=HadithSabrCreateSerializer,
        responses={201: HadithSabrSerializer, 400: {"type": "object"}},
        description="Create a new hadith sabr entry",
        summary="Create hadith sabr entry",
    )
    def post(self, request, *args, **kwargs):
        ser = HadithSabrCreateSerializer(data=request.data, context={"request": request})
        ser.is_valid(raise_exception=True)
        obj = ser.save()
        return Response(_serialize_hadith_sabr(obj), status=status.HTTP_201_CREATED)


@extend_schema(tags=["Hifz"])
class HadithHifzListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsTeacher]

    @extend_schema(
        responses={200: HadithHifzSerializer(many=True)},
        description="List hadith hifz entries for the authenticated teacher's students.",
        summary="List hadith hifz entries",
        parameters=[SYNC_PARAM],
    )
    def get(self, request, *args, **kwargs):
        queryset = (
            HadithHifz.objects.filter(student__teacher=request.user)
            .select_related("student")
            .order_by("-created_at")
        )
        queryset = apply_sync_filter(queryset, request)
        data = [_serialize_hadith_hifz(obj) for obj in queryset]
        return Response(data, status=status.HTTP_200_OK)

    @extend_schema(
        request=HadithHifzCreateSerializer,
        responses={201: HadithHifzSerializer, 400: {"type": "object"}},
        description="Create a new hadith hifz entry",
        summary="Create hadith hifz entry",
    )
    def post(self, request, *args, **kwargs):
        ser = HadithHifzCreateSerializer(data=request.data, context={"request": request})
        ser.is_valid(raise_exception=True)
        obj = ser.save()
        return Response(_serialize_hadith_hifz(obj), status=status.HTTP_201_CREATED)


@extend_schema(tags=["Hifz"], responses={200: HadithHifzSerializer})
class HadithHifzDetailView(APIView):
    permission_classes = [IsAuthenticated, IsTeacher]
    serializer_class = HadithHifzSerializer

    def _get_object(self, request, pk):
        try:
            obj = HadithHifz.objects.select_related("student").get(pk=pk)
        except HadithHifz.DoesNotExist:
            return None, Response({"detail": "Hadith hifz entry not found."}, status=status.HTTP_404_NOT_FOUND)
        if obj.student.teacher_id != request.user.id:
            return None, Response({"detail": "Not yours."}, status=status.HTTP_403_FORBIDDEN)
        return obj, None

    @extend_schema(responses={200: HadithHifzSerializer})
    def get(self, request, pk):
        obj, err = self._get_object(request, pk)
        if err:
            return err
        return Response(_serialize_hadith_hifz(obj), status=status.HTTP_200_OK)

    @extend_schema(request=HadithHifzUpdateSerializer, responses={200: HadithHifzSerializer})
    def put(self, request, pk):
        return self._update(request, pk, partial=False)

    @extend_schema(request=HadithHifzUpdateSerializer, responses={200: HadithHifzSerializer})
    def patch(self, request, pk):
        return self._update(request, pk, partial=True)

    def _update(self, request, pk, partial):
        obj, err = self._get_object(request, pk)
        if err:
            return err
        ser = HadithHifzUpdateSerializer(obj, data=request.data, partial=partial)
        ser.is_valid(raise_exception=True)
        ser.update(obj, ser.validated_data)
        return Response(_serialize_hadith_hifz(obj), status=status.HTTP_200_OK)

    def delete(self, request, pk):
        obj, err = self._get_object(request, pk)
        if err:
            return err
        if not obj.is_deleted:
            obj.is_deleted = True
            obj.save(update_fields=["is_deleted", "updated_at"])
        return Response(status=status.HTTP_204_NO_CONTENT)
