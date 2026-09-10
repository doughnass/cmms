"""Copy MasterItem entries from category 'technician_skill' into 'equipments'.

This migration duplicates existing MasterItem rows that were created under
the 'technician_skill' category (often seeded from Equipment_list.equipment_type)
into a new category 'equipments'. It generates a stable code when missing and
avoids collisions by appending a counter. The forward operation creates new
rows; the reverse operation deletes rows that were created by this migration
by looking for a marker in the description.
"""

from django.db import migrations


def forwards(apps, schema_editor):
    MasterItem = apps.get_model("cmms", "MasterItem")
    from django.utils.text import slugify

    # iterate existing items in technician_skill and create a copy under 'equipments'
    for mi in MasterItem.objects.filter(category="technician_skill"):
        label = (mi.label or "").strip()
        if not label:
            continue

        # prefer existing code; if empty, generate from slug(label)
        base_code = (mi.code or "").strip() or slugify(label)[:50]
        code = base_code
        counter = 1
        while MasterItem.objects.filter(category="equipments", code=code).exists():
            code = f"{base_code}_{counter}"
            counter += 1

        # include a marker in description so the operation can be reversed safely
        desc = mi.description or ""
        marker = f"[copied-from-technician_skill:{mi.pk}]"
        new_desc = (desc + " " + marker).strip()

        MasterItem.objects.create(
            category="equipments",
            code=code,
            label=label,
            description=new_desc,
            active=mi.active,
            order=mi.order,
            parent=None,
        )


def backwards(apps, schema_editor):
    MasterItem = apps.get_model("cmms", "MasterItem")
    # delete only entries created by this migration (those with our marker)
    MasterItem.objects.filter(
        category="equipments", description__contains="[copied-from-technician_skill:"
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("cmms", "0018_seed_technician_skill_masteritems"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
