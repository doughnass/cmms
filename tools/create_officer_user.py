"""Create/update a test officer superuser: e2e_officer / password
Run: python tools\create_officer_user.py
"""

import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cmms_project.settings")
import django

django.setup()
from django.contrib.auth import get_user_model

from cmms.models import ServiceRequest

User = get_user_model()
username = "e2e_officer"
user, created = User.objects.get_or_create(
    username=username, defaults={"email": "e2e_officer@example.local"}
)
if created:
    user.set_password("password")
    user.is_staff = True
    user.is_superuser = True
    user.save()
    print("Created superuser e2e_officer with password: password")
else:
    user.is_staff = True
    user.is_superuser = True
    user.set_password("password")
    user.save()
    print(
        "Updated existing user e2e_officer, set staff/superuser and password to: password"
    )

print("ServiceRequest count =", ServiceRequest.objects.count())
