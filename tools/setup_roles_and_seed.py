"""Setup groups, seed master data, create admin user, and send a test email.
Run: python tools\setup_roles_and_seed.py
"""

import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cmms_project.settings")
import django

django.setup()
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.core.mail import send_mail
from django.template.loader import render_to_string

from cmms.models import MasterItem

User = get_user_model()

# 1) Create groups
groups = {
    "Officer": {
        "perms": [
            "add_workorder",
            "change_workorder",
            "view_workorder",
            "delete_workorder",
            "view_servicerequest",
            "change_servicerequest",
        ]
    },
    "Technician": {
        "perms": [
            "view_workorder",
            "change_workorder",
        ]
    },
    "Engineer": {
        "perms": [
            "view_workorder",
            "change_workorder",
        ]
    },
}

created = []
for gname, data in groups.items():
    g, ok = Group.objects.get_or_create(name=gname)
    created.append((gname, ok))
    # assign permissions by codename
    for codename in data["perms"]:
        try:
            perm = Permission.objects.get(codename=codename)
            g.permissions.add(perm)
        except Permission.DoesNotExist:
            print(f"Permission {codename} not found; skipping")

# 2) Seed MasterItem entries
seed_master = [
    ("workorder_type", "repair", "repair", "ซ่อม"),
    ("workorder_type", "maintenance", "maintenance", "บำรุงรักษา"),
    ("workorder_type", "calibration", "calibration", "สอบเทียบ"),
    ("priority", "low", "low", "ต่ำ"),
    ("priority", "medium", "medium", "ปานกลาง"),
    ("priority", "high", "high", "สูง"),
]
for category, code, label, desc in seed_master:
    MasterItem.objects.get_or_create(
        category=category, code=code, defaults={"label": label, "description": desc}
    )

# 3) Create admin user
admin_username = "admin_local"
admin_email = "admin_local@example.local"
admin_password = "adminpass"
admin, created_admin = User.objects.get_or_create(
    username=admin_username, defaults={"email": admin_email}
)
if created_admin:
    admin.set_password(admin_password)
    admin.is_staff = True
    admin.is_superuser = True
    admin.save()
    print(f"Created admin user {admin_username} with password: {admin_password}")
else:
    # ensure flags set
    admin.is_staff = True
    admin.is_superuser = True
    admin.set_password(admin_password)
    admin.save()
    print(f"Updated admin user {admin_username} (password set to: {admin_password})")

# 4) Send a test email using template if available
try:
    sr_dummy = {"id": 0, "title": "TEST SR", "description": "This is a test"}
    body = render_to_string(
        "emails/sr_created.txt",
        {
            "sr": sr_dummy,
            "site_url": getattr(settings, "SITE_URL", "http://127.0.0.1:8000"),
        },
    )
    send_mail(
        subject="[CMMS TEST] New SR",
        message=body,
        from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
        recipient_list=[admin_email],
        fail_silently=False,
    )
    print("Sent test email to", admin_email)
except Exception as e:
    print("Failed to send test email:", e)

print("\nSetup results:")
print("Groups created/checked:")
for gname, ok in created:
    print(" -", gname)

print("Master items seeded (sample):")
for cat in ("workorder_type", "priority"):
    items = MasterItem.objects.filter(category=cat)
    print(f" - {cat}:", list(items.values_list("label", flat=True)))

print("Done.")
