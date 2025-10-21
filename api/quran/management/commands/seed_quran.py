from django.core.management.base import BaseCommand
from django.db import transaction
from quran.models import Part, Chapter, Verse

from pathlib import Path
import json

def _to_int_or_none(s):
    try:
        return int(str(s).lstrip("0") or "0")
    except (ValueError, TypeError):
        return None


def _parse_verse_tag(tag):
    # "verse_141" -> 141
    if not tag:
        return None
    try:
        return int(str(tag).split("_", 1)[1])
    except Exception:
        return None


class Command(BaseCommand):
    help = "Seeds Chapters and Verses, linking to existing Parts (Juz) based on a chapters JSON file."

    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            type=str,
            help=(
                "Path to a JSON file containing an array of chapter objects. "
                "If omitted, uses quran/management/data/surah.json"
            ),
        )

    @transaction.atomic
    def handle(self, *args, **opts):
        # Default file path: quran/management/data/surah.json
        # __file__ -> .../quran/management/commands/seed_quran_chapters.py
        # parent (commands) -> parent (management) -> data/surah.json
        default_path = (Path(__file__).resolve().parent.parent / "data" / "surah.json")
        path = Path(opts["file"]).resolve() if opts.get("file") else default_path

        if not path.exists():
            self.stderr.write(self.style.ERROR(f"File not found: {path}"))
            return

        # Load JSON (array of chapter objects)
        try:
            # utf-8-sig handles BOM if present
            with path.open("r", encoding="utf-8-sig") as f:
                data = json.load(f)
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Failed to read JSON from {path}: {e}"))
            return

        if not isinstance(data, list):
            self.stderr.write(self.style.ERROR("Expected the JSON root to be an array of chapters."))
            return

        self.stdout.write(self.style.NOTICE(f"Seeding from: {path}"))

        chapters_created = 0
        verses_created_total = 0

        for ch in data:
            ch_index = _to_int_or_none(ch.get("index"))
            if not ch_index:
                self.stderr.write(self.style.WARNING(f"Skipping chapter with invalid index: {ch.get('index')}"))
                continue

            title = ch.get("title") or ""
            ar_title = ch.get("titleAr") or ""
            count = _to_int_or_none(ch.get("count")) or 0

            chapter, created = Chapter.objects.get_or_create(
                index=ch_index,
                defaults={"title": title, "arTitle": ar_title, "totalVerses": count},
            )
            if not created:
                updated = False
                if chapter.title != title:
                    chapter.title = title
                    updated = True
                if chapter.arTitle != ar_title:
                    chapter.arTitle = ar_title
                    updated = True
                if count and chapter.totalVerses != count:
                    chapter.totalVerses = count
                    updated = True
                if updated:
                    chapter.save()
            else:
                chapters_created += 1

            # Link Parts (M2M)
            juz_list = ch.get("juz") or []
            parts_to_add = []
            for j in juz_list:
                p_index = _to_int_or_none(j.get("index"))
                if not p_index:
                    self.stderr.write(self.style.WARNING(f"Chapter {ch_index}: bad part index {j.get('index')}"))
                    continue
                try:
                    part = Part.objects.get(index=p_index)
                except Part.DoesNotExist:
                    self.stderr.write(self.style.ERROR(
                        f"Part (Juz) with index={p_index} does not exist. Seed Parts first."
                    ))
                    continue
                parts_to_add.append(part)

            if parts_to_add:
                chapter.parts.add(*parts_to_add)

            # Create Verses for each Juz's range
            verses_created_for_chapter = 0
            for j in juz_list:
                p_index = _to_int_or_none(j.get("index"))
                if not p_index:
                    continue
                try:
                    part = Part.objects.get(index=p_index)
                except Part.DoesNotExist:
                    continue

                v = j.get("verse") or {}
                start_i = _parse_verse_tag(v.get("start"))
                end_i = _parse_verse_tag(v.get("end"))
                if not start_i or not end_i or end_i < start_i:
                    self.stderr.write(
                        self.style.WARNING(
                            f"Chapter {ch_index}: invalid verse range "
                            f"{v.get('start')}..{v.get('end')} for Juz {p_index}"
                        )
                    )
                    continue

                for i in range(start_i, end_i + 1):
                    _, v_created = Verse.objects.get_or_create(
                        chapter=chapter,
                        part=part,
                        index=i,
                        defaults={"text": ""},
                    )
                    if v_created:
                        verses_created_for_chapter += 1

            verses_created_total += verses_created_for_chapter

            # Sanity check
            if count:
                actual = chapter.verses.count()
                if actual != count:
                    self.stderr.write(
                        self.style.WARNING(
                            f"Chapter {ch_index}: totalVerses={count} but found {actual} Verse rows."
                        )
                    )

            self.stdout.write(
                f"Chapter {ch_index} - {chapter.title}: +{verses_created_for_chapter} verses "
                f"(linked to {len(parts_to_add)} part(s))"
            )

        self.stdout.write(self.style.SUCCESS(
            f"Done. Chapters created: {chapters_created}, Verses created: {verses_created_total}"
        ))
