"""Create users for roles and print randomly generated passwords.
Usage: python tools\create_role_users.py
"""

import os
import secrets
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cmms_project.settings")
import django

django.setup()
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

User = get_user_model()

roles = [
    ("customer", "customer_user"),
    ("officer", "officer_user"),
    ("technician", "technician_user"),
    ("engineer", "engineer_user"),
    ("admin", "admin_user"),
]

created = []
for role, username in roles:
    pwd = secrets.token_urlsafe(10)
    user, created_flag = User.objects.get_or_create(
        username=username, defaults={"email": f"{username}@example.local"}
    )
    user.set_password(pwd)
    # set staff/superuser only for admin
    if role == "admin":
        user.is_staff = True
        user.is_superuser = True
    else:
        user.is_staff = False
        user.is_superuser = False
    user.save()
    # ensure groups exist and assign
    grp_name = None
    if role == "officer":
        grp_name = "Officer"
    if role == "technician":
        grp_name = "Technician"
    if role == "engineer":
        grp_name = "Engineer"
    if role == "customer":
        grp_name = "Customer"
    if grp_name:
        g, gcreated = Group.objects.get_or_create(name=grp_name)
        user.groups.add(g)
    created.append((username, pwd, role))

print("Created/updated users:")
for u, p, r in created:
    print(f" - {u} (role: {r}) password: {p}")

print("\nNotes:")
print(
    " - Admin user is superuser/staff. Change passwords after first login with `python manage.py changepassword <username>`"
)
