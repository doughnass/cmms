"""
Inspect latest WorkOrders and show where data is stored (comments, attachments, logs).
Run with: python tools/inspect_workorders.py
"""

import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cmms_project.settings")
import django

django.setup()
from cmms.models import WorkOrder

wos = WorkOrder.objects.order_by("-reported_at")[:10]
if not wos:
    print("No workorders found in the database.")
else:
    for wo in wos:
        print("---")
        print(f"WO#{wo.id} | Title: {wo.title}")
        print(f"  Status: {wo.status}")
        print(f"  Reported by: {wo.reported_by} at {wo.reported_at}")
        print(f"  Assigned to: {wo.assigned_to}")
        print(f"  Accepted by: {wo.accepted_by} at {wo.accepted_at}")
        print(f"  Technician report: {wo.technician_report}")
        print(f"  Verified by: {wo.verified_by} at {wo.verified_at}")
        print(f"  Notes: {wo.notes}")
        print(f"  Accepted title suggestion: {wo.accepted_title_suggestion}")
        # comments
        comments = list(wo.comments.all())
        print(f"  Comments ({len(comments)}):")
        for c in comments:
            author = c.author.username if c.author else "System"
            print(f"    - [{c.created_at}] {author}: {c.text}")
        # attachments
        attachments = list(wo.attachments.all())
        print(f"  Attachments ({len(attachments)}):")
        for a in attachments:
            print(
                f'    - {a.file.name} uploaded by {a.uploaded_by} at {a.uploaded_at} (path: {a.file.path if hasattr(a.file, "path") else "<no path>"})'
            )
        # logs
        logs = list(wo.logs.order_by("created_at"))
        print(f"  Logs ({len(logs)}):")
        for log in logs:
            actor = log.actor.username if log.actor else "System"
            print(f"    - [{log.created_at}] {log.action} by {actor} : {log.note}")
    print("---")
    print("To view a workorder in the app, open: http://127.0.0.1:8000/workorders/<id>")
    print("Admin path: /admin/cmms/workorder/")
