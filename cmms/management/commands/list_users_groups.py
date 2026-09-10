from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "List users and groups in the system."

    def handle(self, *args, **options):
        User = get_user_model()
        users = User.objects.all()
        groups = Group.objects.all()

        self.stdout.write("Users:")
        for u in users:
            self.stdout.write(
                f" - {u.username} (staff={u.is_staff}, superuser={u.is_superuser})"
            )

        self.stdout.write("\nGroups:")
        for g in groups:
            self.stdout.write(f" - {g.name} (members={g.user_set.count()})")
