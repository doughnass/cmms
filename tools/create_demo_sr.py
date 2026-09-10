"""Create a demo ServiceRequest for testing prefill flow
Run: python tools\create_demo_sr.py
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
user = None
try:
    user = User.objects.filter(is_superuser=True).first()
except Exception:
    pass
sr = ServiceRequest.objects.create(
    title="Demo SR for Prefill",
    description="This request should prefill the WO create form",
    requested_by=user,
)
print("Created SR id", sr.id)
