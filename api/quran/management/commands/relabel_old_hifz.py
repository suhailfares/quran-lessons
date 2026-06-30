from collections import defaultdict

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from quran.models import StudentHifz
from quran.views import _count_memorized_pages


class Command(BaseCommand):
    help = (
        "For each student, finds days where memorized pages (label=MEMORIZATION) "
        "exceed the given threshold and relabels that day's entries to OLD_HIFZ."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--threshold",
            type=int,
            default=6,
            help="Pages-per-day threshold; days strictly greater than this are relabeled (default: 6).",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Print what would change without writing to the database.",
        )

    def handle(self, *args, **options):
        threshold = options["threshold"]
        dry_run = options["dry_run"]

        entries = (
            StudentHifz.objects
            .filter(is_deleted=False, label=StudentHifz.Label.MEMORIZATION)
            .select_related("chapter")
        )

        # group entries by (student_id, day)
        groups = defaultdict(list)
        for e in entries:
            day = e.created_at.date()
            groups[(e.student_id, day)].append(e)

        total_days = 0
        total_rows = 0

        for (student_id, day), day_entries in groups.items():
            chapter_ranges = defaultdict(list)
            for e in day_entries:
                chapter_ranges[e.chapter.index].append((e.start_verse, e.end_verse))

            pages = _count_memorized_pages(chapter_ranges)
            if pages <= threshold:
                continue

            total_days += 1
            total_rows += len(day_entries)
            self.stdout.write(
                f"student={student_id} day={day} pages={pages} rows={len(day_entries)}"
            )

            if not dry_run:
                ids = [e.id for e in day_entries]
                with transaction.atomic():
                    StudentHifz.objects.filter(id__in=ids).update(
                        label=StudentHifz.Label.OLD_HIFZ,
                        updated_at=timezone.now(),
                    )

        action = "Would relabel" if dry_run else "Relabeled"
        self.stdout.write(self.style.SUCCESS(
            f"{action} {total_rows} row(s) across {total_days} student-day(s) "
            f"with > {threshold} pages."
        ))
