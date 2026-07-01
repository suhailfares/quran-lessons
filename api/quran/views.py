# quran/views.py
import json
from collections import defaultdict
from pathlib import Path

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from quran.models import StudentHifz, UserHifz, QuranSabr, Verse
from quran.permissions import IsTeacher
from quran.serializers import (
    StudentHifzCreateSerializer,
    StudentHifzSerializer,
    StudentHifzUpdateSerializer,
    QuranSabrCreateSerializer,
    QuranSabrSerializer,
    UserHifzJuzRangeCreateSerializer,
    UserHifzSerializer,
)
from quranlessons.roles import is_admin, is_strict_admin, is_manager
from quranlessons.sync import apply_sync_filter

_QURAN_PAGES_DATA = json.loads(
    (Path(__file__).parent / "quran_pages.json").read_text(encoding="utf-8")
)["pages"]


def _count_memorized_pages(chapter_ranges):
    """
    chapter_ranges: {chapter_index: [(start_verse, end_verse), ...]}
    Returns count of pages where the student's entries cover >= 50% of the page's verses.
    Uses a set-union per chapter segment to avoid double-counting overlapping entries.
    """
    count = 0
    for page in _QURAN_PAGES_DATA:
        total = page["verses_count"]
        covered = 0
        for chapter_str, range_str in page["verse_mapping"].items():
            chapter_idx = int(chapter_str)
            if chapter_idx not in chapter_ranges:
                continue
            parts = range_str.split("-")
            page_start, page_end = int(parts[0]), int(parts[1])
            covered_verses = set()
            for s, e in chapter_ranges[chapter_idx]:
                overlap_s = max(s, page_start)
                overlap_e = min(e, page_end)
                if overlap_s <= overlap_e:
                    covered_verses.update(range(overlap_s, overlap_e + 1))
            covered += len(covered_verses)
        if covered / total >= 0.75:
            count += 1
    return count


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
        user = request.user
        if is_strict_admin(user):
            queryset = StudentHifz.objects.all()
        elif is_manager(user):
            queryset = StudentHifz.objects.filter(student__teacher__mosque_name=user.mosque_name)
        else:
            queryset = StudentHifz.objects.filter(student__teacher=user)
        queryset = (
            queryset
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
            obj = StudentHifz.objects.select_related("chapter", "student__teacher").get(pk=pk)
        except StudentHifz.DoesNotExist:
            return None, Response({"detail": "Hifz entry not found."}, status=status.HTTP_404_NOT_FOUND)
        user = request.user
        if is_strict_admin(user):
            pass
        elif is_manager(user):
            if obj.student.teacher.mosque_name != user.mosque_name:
                return None, Response({"detail": "Not yours."}, status=status.HTTP_403_FORBIDDEN)
        elif obj.student.teacher_id != user.id:
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
        user = request.user
        if is_strict_admin(user):
            queryset = QuranSabr.objects.all()
        elif is_manager(user):
            queryset = QuranSabr.objects.filter(student__teacher__mosque_name=user.mosque_name)
        else:
            queryset = QuranSabr.objects.filter(student__teacher=user)
        queryset = (
            queryset
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


@extend_schema(
    tags=["Leaderboard"],
    summary="Mosque memorization leaderboard",
    description=(
        "Returns students memorizing Quran in the given mosque, sorted descending by pages memorized. "
        "A page counts if the student's memorization entries (label=حفظ) within the date range "
        "cover >= 50% of that page's verses according to the standard Mushaf layout. "
        "No authentication required."
    ),
    parameters=[
        OpenApiParameter(
            name="mosque",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            required=True,
            description="Exact mosque name to filter by.",
        ),
        OpenApiParameter(
            name="from",
            type=OpenApiTypes.DATE,
            location=OpenApiParameter.QUERY,
            required=False,
            description="Start date (YYYY-MM-DD). Filters by lesson date >= from.",
        ),
        OpenApiParameter(
            name="to",
            type=OpenApiTypes.DATE,
            location=OpenApiParameter.QUERY,
            required=False,
            description="End date (YYYY-MM-DD). Filters by lesson date <= to.",
        ),
    ],
    responses={
        200: {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "student_name": {"type": "string"},
                    "teacher_name": {"type": "string"},
                    "pages": {"type": "integer"},
                },
            },
        },
        400: {"type": "object"},
    },
)
class MosqueLeaderboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        mosque_name = request.query_params.get("mosque", "").strip()
        if not mosque_name:
            return Response(
                {"detail": "Query parameter 'mosque' is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = request.user
        if not is_strict_admin(user) and user.mosque_name != mosque_name:
            return Response({"detail": "Access denied."}, status=status.HTTP_403_FORBIDDEN)

        from_date = request.query_params.get("from", "").strip()
        to_date = request.query_params.get("to", "").strip()

        queryset = StudentHifz.objects.filter(
            is_deleted=False,
            label=StudentHifz.Label.MEMORIZATION,
            student__is_deleted=False,
            student__teacher__mosque_name=mosque_name,
            student__teacher__role="teacher",
        )
        if from_date:
            queryset = queryset.filter(created_at__date__gte=from_date)
        if to_date:
            queryset = queryset.filter(created_at__date__lte=to_date)

        entries = queryset.values(
            "student_id",
            "student__first_name",
            "student__last_name",
            "student__teacher__first_name",
            "student__teacher__last_name",
            "chapter__index",
            "start_verse",
            "end_verse",
        )

        student_info = {}
        student_ranges = defaultdict(lambda: defaultdict(list))

        for entry in entries:
            sid = entry["student_id"]
            if sid not in student_info:
                student_info[sid] = {
                    "student_name": f"{entry['student__first_name']} {entry['student__last_name']}",
                    "teacher_name": f"{entry['student__teacher__first_name']} {entry['student__teacher__last_name']}",
                }
            student_ranges[sid][entry["chapter__index"]].append(
                (entry["start_verse"], entry["end_verse"])
            )

        results = sorted(
            [
                {
                    "student_name": info["student_name"],
                    "teacher_name": info["teacher_name"],
                    "pages": _count_memorized_pages(student_ranges[sid]),
                }
                for sid, info in student_info.items()
            ],
            key=lambda x: x["pages"],
            reverse=True,
        )

        return Response(results, status=status.HTTP_200_OK)


@extend_schema(tags=["User Hifz"])
class UserHifzView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={
            200: {
                "type": "array",
                "items": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "minItems": 2,
                    "maxItems": 2,
                    "example": [1, 5],
                },
            }
        },
        summary="List own hifz as merged juz ranges",
        description=(
            "Returns the user's memorized juz as a list of merged, contiguous ranges. "
            "For example, entries covering juz 1-4 and 3-5 are returned as [[1, 5]]."
        ),
    )
    def get(self, request):
        entries = list(
            UserHifz.objects
            .filter(user=request.user, is_deleted=False)
            .values("chapter_id", "start_verse", "end_verse")
        )
        if not entries:
            return Response([], status=status.HTTP_200_OK)

        from django.db.models import Q
        q = Q()
        for e in entries:
            q |= Q(
                chapter_id=e["chapter_id"],
                index__gte=e["start_verse"],
                index__lte=e["end_verse"],
            )

        covered = sorted(
            Verse.objects.filter(q)
            .values_list("part__index", flat=True)
            .distinct()
        )

        if not covered:
            return Response([], status=status.HTTP_200_OK)

        ranges = []
        start = end = covered[0]
        for juz in covered[1:]:
            if juz == end + 1:
                end = juz
            else:
                ranges.append([start, end])
                start = end = juz
        ranges.append([start, end])

        return Response(ranges, status=status.HTTP_200_OK)

    @extend_schema(
        request=UserHifzJuzRangeCreateSerializer,
        responses={201: UserHifzSerializer(many=True)},
        summary="Create own hifz by juz range",
        description=(
            "Creates hifz entries for the authenticated user covering all chapters "
            "within the given juz range. Each chapter gets one entry with the verse "
            "range that falls inside the requested juz."
        ),
    )
    def post(self, request):
        ser = UserHifzJuzRangeCreateSerializer(data=request.data, context={"request": request})
        ser.is_valid(raise_exception=True)
        entries = ser.save()
        data = [UserHifzSerializer(e).data for e in entries]
        return Response(data, status=status.HTTP_201_CREATED)
