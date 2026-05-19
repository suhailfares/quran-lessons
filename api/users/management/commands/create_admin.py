import os
from django.core.management.base import BaseCommand
from users.models import User


class Command(BaseCommand):
    help = "Create or update an admin account from environment variables"

    def handle(self, *args, **options):
        password = os.getenv("ADMIN_PASSWORD")
        if not password:
            self.stdout.write(
                self.style.ERROR("Error: ADMIN_PASSWORD environment variable not set")
            )
            return

        user, created = User.objects.get_or_create(
            username="admin",
            defaults={
                "first_name": "Admin",
                "last_name": "User",
                "role": "admin",
            },
        )

        user.set_password(password)
        user.save()

        if created:
            self.stdout.write(
                self.style.SUCCESS("Successfully created admin account")
            )
        else:
            self.stdout.write(
                self.style.SUCCESS("Successfully updated admin account password")
            )
