"""Copy Technician.skills_m relations from technician_skill MasterItem to equipments MasterItem.

For each Technician, find their related MasterItem(s) in category 'technician_skill'. For each such
MasterItem, find a MasterItem in category 'equipments' with the same label (should exist due to 0019)
and add it to the technician.skills_m relation. This preserves existing mappings while keeping the
original relations intact (do not remove old links in case a rollback is desired).
"""

from django.db import migrations


def forwards(apps, schema_editor):
    Technician = apps.get_model("cmms", "Technician")
    MasterItem = apps.get_model("cmms", "MasterItem")

    for tech in Technician.objects.all():
        # gather labels from related technician_skill items
        tech_skill_items = tech.skills_m.filter(category="technician_skill")
        for mi in tech_skill_items:
            label = mi.label
            if not label:
                continue
            # find matching equipments MasterItem (prefer exact label match)
            target = MasterItem.objects.filter(
                category="equipments", label__iexact=label
            ).first()
            if target:
                tech.skills_m.add(target)


def backwards(apps, schema_editor):
    # reverse: remove relations that point to equipments items that were copied (those with marker)
    Technician = apps.get_model("cmms", "Technician")
    MasterItem = apps.get_model("cmms", "MasterItem")

    copied = MasterItem.objects.filter(
        category="equipments", description__contains="[copied-from-technician_skill:"
    )
    for tech in Technician.objects.all():
        for mi in copied:
            tech.skills_m.remove(mi)


class Migration(migrations.Migration):

    dependencies = [
        ("cmms", "0020_alter_technician_skillsm_limitchoices"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
