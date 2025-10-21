from django.core.management import BaseCommand

from quran.models import Part


class Command(BaseCommand):
    help = "Seeds the database with the 30 Parts in the Holy Quran."

    def handle(self, *args, **options):
        parts_data = [
            {
                "index": i,
                "title": f"Juz {i}",
                "arTitle": f"الجزء {i}"
            }
            for i in range(1, 31)
        ]

        created_count = 0
        for data in parts_data:
            part, created = Part.objects.get_or_create(
                index=data["index"],
                defaults={
                    "title": data["title"],
                    "arTitle": data["arTitle"],
                },
            )
            if created:
                created_count += 1

            self.stdout.write(
                self.style.SUCCESS(f"Successfully seeded {created_count} Parts (Juz).")
            )




