from collections import defaultdict
from datetime import date as date_cls
from http import HTTPStatus

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from hadith.models import HadithHifz, HadithSabr
from lessons.models import Attendance
from quran.models import QuranSabr, StudentHifz
from quranlessons.roles import is_manager, is_strict_admin
from students.models import Student
from users.models import User
from users.permissions import IsAdmin

VALID_FIELDS = {
    "attendance",
    "quran_hifz",
    "hadith_hifz",
    "sabr_awqaf",
    "sabr_institute",
    "sabr_cumulative",
    "sabr_hadith",
}

# Order used for sort-field selection (attendance excluded)
_SORT_FIELD_PRIORITY = [
    "quran_hifz",
    "hadith_hifz",
    "sabr_awqaf",
    "sabr_institute",
    "sabr_cumulative",
    "sabr_hadith",
]

_SABR_FIELD_TO_TYPE = {
    "sabr_awqaf":      QuranSabr.Type.AWQAF,
    "sabr_institute":  QuranSabr.Type.INSTITUTE,
    "sabr_cumulative": QuranSabr.Type.CUMULATIVE_INSTITUTE,
}


def _parse_date_param(raw):
    if raw is None:
        return None
    try:
        return date_cls.fromisoformat(raw)
    except ValueError:
        return ...


def _resolve_teachers(request, teacher_id_raw):
    """Return (teacher_ids: list[int] | None, single_teacher: User | None).

    teacher_ids=None means no teacher restriction (strict admin, no teacher_id given).
    """
    user = request.user

    if teacher_id_raw is not None:
        try:
            tid = int(teacher_id_raw)
        except (ValueError, TypeError):
            return None, None, Response(
                {"detail": "teacher_id must be an integer."},
                status=HTTPStatus.BAD_REQUEST,
            )
        try:
            teacher = User.objects.get(pk=tid, role="teacher")
        except User.DoesNotExist:
            return None, None, Response(
                {"detail": "Teacher not found."},
                status=HTTPStatus.NOT_FOUND,
            )
        if is_manager(user) and teacher.mosque_name != user.mosque_name:
            return None, None, Response(
                {"detail": "Teacher does not belong to your mosque."},
                status=HTTPStatus.FORBIDDEN,
            )
        return [tid], teacher, None

    # No teacher_id provided
    if is_manager(user):
        ids = list(
            User.objects.filter(role="teacher", mosque_name=user.mosque_name)
            .values_list("id", flat=True)
        )
        return ids, None, None

    # Strict admin with no teacher_id → unrestricted
    return None, None, None


def _build_student_entry(student, fields, att_map, hifz_map, hadith_hifz_map,
                         qsabr_map, hsabr_map):
    sid = student.id
    entry = {
        "student_id": sid,
        "first_name": student.first_name,
        "last_name": student.last_name,
    }
    if "attendance" in fields:
        entry["attendance"] = [
            {
                "lesson_id":   a.lesson_id,
                "lesson_name": a.lesson.subject,
                "attended":    a.attended,
                "date":        str(a.date),
            }
            for a in att_map.get(sid, [])
        ]
    if "quran_hifz" in fields:
        entry["quran_hifz"] = [
            {
                "chapter_index": h.chapter.index,
                "chapter_title": h.chapter.arTitle or h.chapter.title,
                "start_verse":   h.start_verse,
                "end_verse":     h.end_verse,
                "label":         h.label,
                "date":          h.created_at.isoformat(),
            }
            for h in hifz_map.get(sid, [])
        ]
    if "hadith_hifz" in fields:
        entry["hadith_hifz"] = [
            {
                "hadith_numbers": h.hadith_numbers,
                "label":          h.label,
                "notes":          h.notes,
                "date":           h.created_at.isoformat(),
            }
            for h in hadith_hifz_map.get(sid, [])
        ]
    for field_key, sabr_type_val in _SABR_FIELD_TO_TYPE.items():
        if field_key in fields:
            entry[field_key] = [
                {
                    "range_start": q.range_start,
                    "range_end":   q.range_end,
                    "created_at":  q.created_at.isoformat(),
                }
                for q in qsabr_map.get(sid, {}).get(sabr_type_val, [])
            ]
    if "sabr_hadith" in fields:
        entry["sabr_hadith"] = [
            {
                "hadith_type": h.hadith_type,
                "created_at":  h.created_at.isoformat(),
            }
            for h in hsabr_map.get(sid, [])
        ]
    return entry


@extend_schema(
    tags=["Reports"],
    summary="Manager / admin student activity report",
    description=(
        "Returns selected activity data for students belonging to teacher(s) in the "
        "manager's mosque (or all for strict admin). Two modes:\n\n"
        "**Mode A** — `teacher_id` provided AND `date_from == date_to`: students grouped "
        "by lesson (lesson membership derived from attendance records).\n\n"
        "**Mode B** — date range OR all teachers: flat list sorted descending by count of "
        "the first non-attendance selected field."
    ),
    parameters=[
        OpenApiParameter(
            "date_from", OpenApiTypes.DATE, OpenApiParameter.QUERY, required=True,
            description="Start of the date range (YYYY-MM-DD).",
        ),
        OpenApiParameter(
            "date_to", OpenApiTypes.DATE, OpenApiParameter.QUERY, required=True,
            description="End of the date range (YYYY-MM-DD). Equal to date_from for a single day.",
        ),
        OpenApiParameter(
            "teacher_id", OpenApiTypes.INT, OpenApiParameter.QUERY, required=False,
            description="Filter to a single teacher. Manager: must be in their mosque.",
        ),
        OpenApiParameter(
            "fields", OpenApiTypes.STR, OpenApiParameter.QUERY, required=True,
            description=(
                "Comma-separated list of data types to include. "
                "Valid values: attendance, quran_hifz, hadith_hifz, "
                "sabr_awqaf, sabr_institute, sabr_cumulative, sabr_hadith."
            ),
        ),
    ],
    responses={200: {"type": "object"}, 400: {"type": "object"}, 403: {"type": "object"}},
)
class ReportView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        # --- 1. Parse & validate dates ---
        date_from = _parse_date_param(request.query_params.get("date_from"))
        date_to   = _parse_date_param(request.query_params.get("date_to"))

        if date_from is None or date_to is None:
            return Response(
                {"detail": "date_from and date_to are required (YYYY-MM-DD)."},
                status=HTTPStatus.BAD_REQUEST,
            )
        if date_from is ... or date_to is ...:
            return Response(
                {"detail": "date_from and date_to must be valid dates (YYYY-MM-DD)."},
                status=HTTPStatus.BAD_REQUEST,
            )
        if date_from > date_to:
            return Response(
                {"detail": "date_from must not be later than date_to."},
                status=HTTPStatus.BAD_REQUEST,
            )

        # --- 2. Parse & validate fields ---
        fields_raw = request.query_params.get("fields", "")
        fields = {f.strip() for f in fields_raw.split(",") if f.strip()}
        if not fields:
            return Response(
                {"detail": f"fields is required. Valid values: {', '.join(sorted(VALID_FIELDS))}."},
                status=HTTPStatus.BAD_REQUEST,
            )
        unknown = fields - VALID_FIELDS
        if unknown:
            return Response(
                {"detail": f"Unknown field(s): {', '.join(sorted(unknown))}. Valid values: {', '.join(sorted(VALID_FIELDS))}."},
                status=HTTPStatus.BAD_REQUEST,
            )

        # --- 3. Resolve teacher scope ---
        teacher_id_raw = request.query_params.get("teacher_id")
        teacher_ids, single_teacher, err = _resolve_teachers(request, teacher_id_raw)
        if err:
            return err

        # --- 4. Fetch students ---
        qs = Student.objects.filter(is_deleted=False).select_related("teacher")
        if teacher_ids is not None:
            qs = qs.filter(teacher_id__in=teacher_ids)
        students = list(qs)
        student_ids = [s.id for s in students]
        student_map = {s.id: s for s in students}

        if not student_ids:
            return self._empty_response(
                mode_a=(teacher_id_raw is not None and date_from == date_to),
                date_from=date_from,
                date_to=date_to,
                single_teacher=single_teacher,
            )

        # --- 5. Bulk-fetch domain data ---
        att_map          = defaultdict(list)
        hifz_map         = defaultdict(list)
        hadith_hifz_map  = defaultdict(list)
        qsabr_map        = defaultdict(lambda: defaultdict(list))
        hsabr_map        = defaultdict(list)

        if "attendance" in fields:
            for a in (
                Attendance.objects
                .filter(student_id__in=student_ids, date__range=(date_from, date_to), is_deleted=False)
                .select_related("lesson")
                .order_by("date")
            ):
                att_map[a.student_id].append(a)

        if "quran_hifz" in fields:
            for h in (
                StudentHifz.objects
                .filter(
                    student_id__in=student_ids,
                    created_at__date__gte=date_from,
                    created_at__date__lte=date_to,
                    is_deleted=False,
                )
                .select_related("chapter")
                .order_by("created_at")
            ):
                hifz_map[h.student_id].append(h)

        if "hadith_hifz" in fields:
            for h in (
                HadithHifz.objects
                .filter(
                    student_id__in=student_ids,
                    created_at__date__gte=date_from,
                    created_at__date__lte=date_to,
                    is_deleted=False,
                )
                .order_by("created_at")
            ):
                hadith_hifz_map[h.student_id].append(h)

        requested_sabr_types = [
            _SABR_FIELD_TO_TYPE[f] for f in fields if f in _SABR_FIELD_TO_TYPE
        ]
        if requested_sabr_types:
            for q in (
                QuranSabr.objects
                .filter(
                    student_id__in=student_ids,
                    sabr_type__in=requested_sabr_types,
                    created_at__date__gte=date_from,
                    created_at__date__lte=date_to,
                    is_deleted=False,
                )
                .order_by("created_at")
            ):
                qsabr_map[q.student_id][q.sabr_type].append(q)

        if "sabr_hadith" in fields:
            for h in (
                HadithSabr.objects
                .filter(
                    student_id__in=student_ids,
                    created_at__date__gte=date_from,
                    created_at__date__lte=date_to,
                    is_deleted=False,
                )
                .order_by("created_at")
            ):
                hsabr_map[h.student_id].append(h)

        domain_maps = (att_map, hifz_map, hadith_hifz_map, qsabr_map, hsabr_map)

        # --- 6. Filter to students with at least one record ---
        active_ids = (
            set(att_map) | set(hifz_map) | set(hadith_hifz_map)
            | set(qsabr_map) | set(hsabr_map)
        )
        active_students = [s for s in students if s.id in active_ids]

        # --- 7. Build response ---
        mode_a = (teacher_id_raw is not None) and (date_from == date_to)

        if mode_a:
            return self._mode_a_response(
                active_students, student_ids, fields, domain_maps,
                single_teacher, date_from,
            )
        return self._mode_b_response(
            active_students, fields, domain_maps, date_from, date_to,
        )

    # ------------------------------------------------------------------
    # Mode A
    # ------------------------------------------------------------------

    def _mode_a_response(self, active_students, all_student_ids, fields,
                         domain_maps, teacher, date):
        att_map = domain_maps[0]

        # Fetch attendance for lesson grouping (regardless of whether attendance is in fields)
        grouping_qs = (
            Attendance.objects
            .filter(
                student_id__in=all_student_ids,
                date=date,
                is_deleted=False,
            )
            .select_related("lesson")
        )
        # lesson_id → (lesson_id, lesson_name)
        lesson_meta = {}
        # student_id → list of lesson_ids
        student_to_lessons = defaultdict(list)
        for a in grouping_qs:
            lesson_meta[a.lesson_id] = (a.lesson_id, a.lesson.subject)
            student_to_lessons[a.student_id].append(a.lesson_id)

        active_set = {s.id for s in active_students}
        student_map_local = {s.id: s for s in active_students}

        # Build lesson → student list (only active students)
        lesson_to_sids = defaultdict(list)
        no_lesson_sids = []
        for sid in active_set:
            lessons = student_to_lessons.get(sid)
            if lessons:
                for lid in lessons:
                    lesson_to_sids[lid].append(sid)
            else:
                no_lesson_sids.append(sid)

        lessons_out = []
        for lid, (lesson_id, lesson_name) in lesson_meta.items():
            sids = lesson_to_sids.get(lid, [])
            if not sids:
                continue
            lessons_out.append({
                "lesson_id":   lesson_id,
                "lesson_name": lesson_name,
                "students": [
                    _build_student_entry(student_map_local[sid], fields, *domain_maps)
                    for sid in sids
                ],
            })

        if no_lesson_sids:
            lessons_out.append({
                "lesson_id":   None,
                "lesson_name": None,
                "students": [
                    _build_student_entry(student_map_local[sid], fields, *domain_maps)
                    for sid in no_lesson_sids
                ],
            })

        return Response({
            "mode":         "single_teacher_single_day",
            "date":         str(date),
            "teacher_id":   teacher.id if teacher else None,
            "teacher_name": f"{teacher.first_name} {teacher.last_name}" if teacher else None,
            "lessons":      lessons_out,
        })

    # ------------------------------------------------------------------
    # Mode B
    # ------------------------------------------------------------------

    def _mode_b_response(self, active_students, fields, domain_maps, date_from, date_to):
        att_map = domain_maps[0]

        # Determine sort field
        sort_field = next(
            (f for f in _SORT_FIELD_PRIORITY if f in fields),
            "attendance",
        )

        rows = []
        for student in active_students:
            entry = _build_student_entry(student, fields, *domain_maps)
            entry["teacher_id"]   = student.teacher_id
            entry["teacher_name"] = (
                f"{student.teacher.first_name} {student.teacher.last_name}"
                if student.teacher_id else None
            )
            rows.append(entry)

        rows.sort(key=lambda r: len(r.get(sort_field, [])), reverse=True)

        return Response({
            "mode":      "range_or_multi_teacher",
            "date_from": str(date_from),
            "date_to":   str(date_to),
            "students":  rows,
        })

    # ------------------------------------------------------------------
    # Empty result helpers
    # ------------------------------------------------------------------

    def _empty_response(self, *, mode_a, date_from, date_to, single_teacher):
        if mode_a:
            return Response({
                "mode":         "single_teacher_single_day",
                "date":         str(date_from),
                "teacher_id":   single_teacher.id if single_teacher else None,
                "teacher_name": (
                    f"{single_teacher.first_name} {single_teacher.last_name}"
                    if single_teacher else None
                ),
                "lessons": [],
            })
        return Response({
            "mode":      "range_or_multi_teacher",
            "date_from": str(date_from),
            "date_to":   str(date_to),
            "students":  [],
        })
