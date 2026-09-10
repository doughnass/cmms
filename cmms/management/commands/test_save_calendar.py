
from django.core.management.base import BaseCommand
from django.test import Client
from django.urls import reverse
from django.utils import timezone


class Command(BaseCommand):
    help = "Simulate posting calendar save from manage UI and report DB results"

    def add_arguments(self, parser):
        parser.add_argument(
            "--tech-id", type=int, required=True, help="Technician id to test"
        )
        parser.add_argument("--month", type=int, help="Month number (1-12)")
        parser.add_argument("--year", type=int, help="Year (e.g., 2025)")
        parser.add_argument(
            "--days", type=int, nargs="+", help="Days to set as working (e.g., 1 2 3)"
        )

    def handle(self, *args, **options):
        tech_id = options["tech_id"]
        today = timezone.localtime().date()
        month = options.get("month") or today.month
        year = options.get("year") or today.year
        days = options.get("days") or [1, 2, 3]

        client = Client()
        url = reverse("technician_availability_manage")

        # Ensure the client is authenticated as a user with permission to post
        try:
            from django.contrib.auth import get_user_model

            User = get_user_model()
            admin = User.objects.filter(is_superuser=True).first()
            if not admin:
                # create a temporary superuser for testing
                admin = User.objects.create_superuser(
                    "testsys", "test@example.com", "testpass"
                )
            client.force_login(admin)
        except Exception:
            # If auth models differ or creation fails, continue unauthenticated
            pass

        # Build post data
        post = {
            "month": str(month),
            "year": str(year),
        }

        for d in days:
            post[f"status_{tech_id}_{d}"] = "work_regular"
            # Example: set overtime for first day
            if d == days[0]:
                post[f"overtime_{tech_id}_{d}"] = "1"

        print("Posting to", url)
        # Provide a valid Host header to avoid DisallowedHost in test environments
        resp = client.post(url, post, follow=True, HTTP_HOST="localhost")
        print("Response status code:", resp.status_code)

        # Report DB state
        from cmms.models import TechnicianAvailability

        avails = TechnicianAvailability.objects.filter(
            technician_id=tech_id, date__year=year, date__month=month
        ).order_by("date")
        print(
            f"Found {avails.count()} availabilities for tech {tech_id} in {year}-{month:02d}"
        )
        for a in avails:
            print("-", a.date.isoformat(), a.status, a.note)

        self.stdout.write(self.style.SUCCESS("Test save_calendar completed"))
