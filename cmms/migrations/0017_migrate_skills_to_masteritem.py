"""Data migration: migrate Technician.skills (comma-separated text) to Technician.skills_m (M2M to MasterItem).

Creates MasterItem rows in category 'technician_skill' for any skill labels not already present,
then links them to the Technician via skills_m.

Reverse operation will copy back labels into Technician.skills as comma-separated list.
"""

from django.db import migrations


def forwards(apps, schema_editor):
    Technician = apps.get_model("cmms", "Technician")
    MasterItem = apps.get_model("cmms", "MasterItem")

    for tech in Technician.objects.all():
        skills_text = getattr(tech, "skills", None)
        if not skills_text:
            continue
        parts = [s.strip() for s in skills_text.split(",") if s and s.strip()]
        for label in parts:
            mi, created = MasterItem.objects.get_or_create(
                category="technician_skill",
                label=label,
                defaults={"code": "", "description": "", "active": True, "order": 0},
            )
            tech.skills_m.add(mi)


def backwards(apps, schema_editor):
    Technician = apps.get_model("cmms", "Technician")

    for tech in Technician.objects.all():
        # generate comma-separated labels from skills_m
        labels = [mi.label for mi in tech.skills_m.all()]
        tech.skills = ",".join(labels)
        tech.save()


class Migration(migrations.Migration):

    dependencies = [
        ("cmms", "0016_technician_skills_m"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
