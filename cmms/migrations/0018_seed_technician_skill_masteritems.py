"""Seed MasterItem entries for category 'technician_skill' using distinct equipment_type values."""

from django.db import migrations


def forwards(apps, schema_editor):
    MasterItem = apps.get_model("cmms", "MasterItem")
    Equipment_list = apps.get_model("cmms", "Equipment_list")

    types = Equipment_list.objects.values_list("equipment_type", flat=True).distinct()
    for t in types:
        if not t:
            continue
        label = t.strip()
        MasterItem.objects.get_or_create(
            category="technician_skill",
            label=label,
            defaults={
                "code": "",
                "description": f"จาก equipment_type: {label}",
                "active": True,
                "order": 0,
            },
        )


def backwards(apps, schema_editor):
    # do not delete automatically created items
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("cmms", "0017_migrate_skills_to_masteritem"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
