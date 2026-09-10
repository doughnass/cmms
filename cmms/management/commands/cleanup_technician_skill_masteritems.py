from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Safely delete MasterItem entries in category technician_skill that are unused. Use --dry-run to preview."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Do not delete, just show what would be deleted",
        )

    def handle(self, *args, **options):
        from cmms.models import MasterItem

        candidates = MasterItem.objects.filter(category="technician_skill")
        to_delete = []
        for mi in candidates:
            has_tech = mi.technicians.exists()
            has_marker = (
                mi.description and "[copied-from-technician_skill:" in mi.description
            )
            if not has_tech and not has_marker:
                to_delete.append(mi)

        self.stdout.write(
            f"Found {len(to_delete)} technician_skill MasterItem(s) eligible for deletion"
        )
        for mi in to_delete:
            self.stdout.write(f' - ID {mi.id}: {mi.label} (code="{mi.code}")')

        if options.get("dry_run"):
            self.stdout.write(self.style.SUCCESS("Dry run complete — no changes made."))
            return

        if not to_delete:
            self.stdout.write("Nothing to delete.")
            return

        confirm = input("Delete these items? type YES to proceed: ")
        if confirm == "YES":
            ids = [mi.id for mi in to_delete]
            MasterItem.objects.filter(id__in=ids).delete()
            self.stdout.write(self.style.SUCCESS(f"Deleted {len(ids)} items."))
        else:
            self.stdout.write("Aborted.")
