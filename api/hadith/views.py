from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from hadith.models import HadithSabr
from hadith.permissions import IsTeacher
from hadith.serializers import (
    HadithSabrCreateSerializer,
    HadithSabrSerializer,
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
