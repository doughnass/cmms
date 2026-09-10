from django.core.management import call_command
from django.test import TestCase

from cmms.models import MasterItem, Technician


class MigrateSkillsCommandTests(TestCase):
    def test_migrate_creates_masteritems_and_links(self):
        # create technician with legacy comma-separated skills
        t = Technician.objects.create(
            name="Legacy Tech",
            skills="Ventilator, X-Ray ",
            phone="000",
            per_day_capacity=1,
            active=True,
        )
        # ensure no MasterItem exists yet
        self.assertEqual(
            MasterItem.objects.filter(category="technician_skill").count(), 0
        )
        # run command (not dry-run)
        call_command("migrate_skills_to_master")
        # now expect MasterItems created
        self.assertTrue(
            MasterItem.objects.filter(
                category="technician_skill", label__iexact="Ventilator"
            ).exists()
        )
        self.assertTrue(
            MasterItem.objects.filter(
                category="technician_skill", label__iexact="X-Ray"
            ).exists()
        )
        # tech should have skills_m relations
        t.refresh_from_db()
        labels = set(t.skills_m.values_list("label", flat=True))
        self.assertIn("Ventilator", labels)
        self.assertIn("X-Ray", labels)
