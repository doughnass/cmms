from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create a non-interactive development superuser (devadmin/devpass) if it does not exist."

    def handle(self, *args, **options):
        User = get_user_model()
        username = "devadmin"
        email = "devadmin@example.com"
        password = "devpass"

        user, created = User.objects.get_or_create(
            username=username, defaults={"email": email}
        )
        if created:
            user.set_password(password)
            user.is_staff = True
            user.is_superuser = True
            user.save()
            self.stdout.write(
                self.style.SUCCESS(
                    f"Created superuser '{username}' with password '{password}'"
                )
            )
        else:
            changed = False
            if not user.is_superuser:
                user.is_superuser = True
                changed = True
            if not user.is_staff:
                user.is_staff = True
                changed = True
            if changed:
                user.save()
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Updated existing user '{username}' to staff+superuser"
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f"User '{username}' already exists")
                )
