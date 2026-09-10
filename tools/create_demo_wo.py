"""Create a demo WorkOrder, a comment, a log entry and attach media/demo/sample_attachment.txt
Run from the project root: python tools\create_demo_wo.py
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
from django.core.files.base import ContentFile

from cmms.models import (WorkOrder, WorkOrderAttachment, WorkOrderComment,
                         WorkOrderLog)

User = get_user_model()
# Create or get demo user
u, created = User.objects.get_or_create(
    username="demo_requester", defaults={"email": "demo@example.local"}
)
if created:
    u.set_password("password")
    u.save()
    print("Created user demo_requester")
else:
    print("Using existing user demo_requester")
# Create WorkOrder
wo = WorkOrder.objects.create(title="Demo Request From User", reported_by=u)
WorkOrderLog.objects.create(
    workorder=wo, action="created", actor=u, note="Initial request (demo)"
)
# Add comment
WorkOrderComment.objects.create(
    workorder=wo, author=u, text="Please check this equipment (demo)"
)
# Attach file if exists
p = os.path.join(ROOT, "media", "demo", "sample_attachment.txt")
if os.path.exists(p):
    with open(p, "rb") as f:
        wa = WorkOrderAttachment.objects.create(workorder=wo, uploaded_by=u)
        wa.file.save("sample_attachment.txt", ContentFile(f.read()))
        wa.save()
    print("Attached file to WorkOrder")
else:
    print("Attachment file not found:", p)

print("Created demo WorkOrder id", wo.id)
print("Title:", wo.title)
print("Attachments:", list(wo.attachments.values_list("file", flat=True)))
print("Logs:", list(wo.logs.values_list("action", "note")))
