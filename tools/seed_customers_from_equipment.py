"""Seed MasterItem entries (category 'customers') from Equipment_list fields.
Run: python tools\seed_customers_from_equipment.py
"""

import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cmms_project.settings")
import django

django.setup()
from cmms.models import Equipment_list, MasterItem

# fields to scan for customer values
fields = ["equipment_user_customer", "equipment_owner_customer"]
values = set()
for f in fields:
    # collect distinct values via ORM
    qs = (
        Equipment_list.objects.exclude(**{f: ""})
        .exclude(**{f: None})
        .values_list(f, flat=True)
    )
    for v in qs:
        if v is None:
            continue
        s = str(v).strip()
        if s:
            values.add(s)

print(f"Found {len(values)} unique customer names from equipment fields.")
created = 0
skipped = 0
for v in sorted(values):
    # create MasterItem with category 'customers', code generated from label
    code = "".join(c for c in v.lower() if c.isalnum() or c in ("-", "_"))[:50]
    try:
        mi, ok = MasterItem.objects.get_or_create(
            category="customers",
            code=code,
            defaults={"label": v, "description": "Imported from Equipment_list field"},
        )
        if ok:
            created += 1
            print("Created MasterItem:", mi.label)
        else:
            skipped += 1
    except Exception as e:
        print("Error creating MasterItem for", v, e)

print("\nDone. Created:", created, "Skipped(existing):", skipped)
