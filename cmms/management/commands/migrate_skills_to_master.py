from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Migrate legacy Technician.skills (comma-separated labels) into MasterItem rows (category=technician_skill) and populate skills_m relations."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Do not save changes; just print what would be done",
        )

    def handle(self, *args, **options):
        from cmms.models import MasterItem, Technician

        dry = options.get("dry_run")
        self.stdout.write("Scanning technicians for legacy skills...")
        created = 0
        linked = 0
        from django.utils.text import slugify

        for t in Technician.objects.all():
            raw = (t.skills or "").strip()
            if not raw:
                continue
            labels = [s.strip() for s in raw.split(",") if s.strip()]
            if not labels:
                continue
            self.stdout.write(f"Technician {t.id} {t.name}: found labels {labels}")
            for lab in labels:
                mi = MasterItem.objects.filter(
                    category="technician_skill", label__iexact=lab
                ).first()
                if not mi:
                    # generate a slug code from label and ensure uniqueness within category
                    base_code = slugify(lab) or "skill"
                    code = base_code
                    i = 1
                    while MasterItem.objects.filter(
                        category="technician_skill", code=code
                    ).exists():
                        i += 1
                        code = f"{base_code}-{i}"
                    self.stdout.write(
                        f'  Creating MasterItem for label: "{lab}" with code "{code}"'
                    )
                    if not dry:
                        mi = MasterItem.objects.create(
                            category="technician_skill",
                            code=code,
                            label=lab,
                            active=True,
                        )
                        created += 1
                if mi:
                    if not dry:
                        t.skills_m.add(mi)
                        linked += 1

        self.stdout.write(
            f"Done. Created MasterItem: {created}, linked skills: {linked}"
        )
