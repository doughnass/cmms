from django.core.management.base import BaseCommand
from django.db import models


class Command(BaseCommand):
    help = "Report MasterItem copy counts created by migration 0019 and summary of technician_skill vs equipments"

    def handle(self, *args, **options):
        from cmms.models import MasterItem

        copied = MasterItem.objects.filter(
            category="equipments",
            description__contains="[copied-from-technician_skill:",
        )
        total_copied = copied.count()

        total_equip = MasterItem.objects.filter(category="equipments").count()
        total_tech = MasterItem.objects.filter(category="technician_skill").count()

        tech_with_rel = (
            MasterItem.objects.filter(category="technician_skill")
            .annotate(num_tech=models.Count("technicians"))
            .filter(num_tech__gt=0)
            .count()
        )

        self.stdout.write(
            self.style.SUCCESS(f"Copied entries (marker): {total_copied}")
        )
        self.stdout.write(f"Total equipments MasterItem: {total_equip}")
        self.stdout.write(f"Total technician_skill MasterItem: {total_tech}")
        self.stdout.write(
            f"Technician_skill items that still have technician relations: {tech_with_rel}"
        )
