import os

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Create or update a Newsline administrator account."

    def add_arguments(self, parser):
        parser.add_argument("--username", default=os.getenv("ADMIN_USERNAME", "bkisak101@gmail.com"))
        parser.add_argument("--password", default=os.getenv("ADMIN_PASSWORD"))
        parser.add_argument("--email", default=os.getenv("ADMIN_EMAIL", ""))

    def handle(self, *args, **options):
        password = options["password"]
        if not password:
            raise CommandError("Provide --password or set ADMIN_PASSWORD.")
        user = User.objects.filter(username=options["username"]).first() or User(username=options["username"])
        user.email = options["email"] or user.email
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.set_password(password)
        user.save()
        self.stdout.write(self.style.SUCCESS(f"Administrator ready: {user.username}"))
