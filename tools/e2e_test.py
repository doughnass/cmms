"""
Simple end-to-end workflow test script for the CMMS project.
Creates 4 users (if missing): e2e_requester, e2e_officer, e2e_tech, e2e_engineer
Creates a WorkOrder and performs: accept, assign, tech start, tech complete, engineer verify.
Prints the final workorder fields and the WorkOrderLog entries.

Run with: python tools/e2e_test.py
"""

import os
import sys

import django

# Ensure project root is on sys.path
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cmms_project.settings")
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone

from cmms.models import WorkOrder, WorkOrderLog

User = get_user_model()


def get_or_create_user(username, email, is_staff=False):
    user, created = User.objects.get_or_create(
        username=username, defaults={"email": email}
    )
    if created:
        user.set_password("password")
        user.is_staff = is_staff
        user.save()
        print(f"Created user: {username}")
    else:
        print(f"User exists: {username}")
    return user


def main():
    print("Starting E2E workflow test")
    requester = get_or_create_user("e2e_requester", "e2e_requester@example.local")
    officer = get_or_create_user(
        "e2e_officer", "e2e_officer@example.local", is_staff=True
    )
    tech = get_or_create_user("e2e_tech", "e2e_tech@example.local")
    engineer = get_or_create_user("e2e_engineer", "e2e_engineer@example.local")

    # Create workorder
    wo = WorkOrder.objects.create(
        title="E2E Test WorkOrder " + timezone.now().strftime("%Y%m%d%H%M%S"),
        reported_by=requester,
    )
    print(f"Created WorkOrder #{wo.id} (status={wo.status})")

    now = timezone.now()

    # Officer accepts
    wo.accepted_by = officer
    wo.accepted_at = now
    wo.accepted_note = "Officer accepted for test"
    wo.status = "assigned"
    wo.save()
    WorkOrderLog.objects.create(
        workorder=wo, action="accepted", actor=officer, note=wo.accepted_note
    )
    print("Officer accepted and set status to assigned")

    # Assign to tech (redundant, but create a log entry)
    wo.assigned_to = tech
    wo.save()
    WorkOrderLog.objects.create(
        workorder=wo,
        action="assigned",
        actor=officer,
        note=f"Assigned to {tech.username}",
    )
    print(f"Assigned to tech: {tech.username}")

    # Tech starts
    wo.actual_start = timezone.now()
    wo.status = "in_progress"
    wo.save()
    WorkOrderLog.objects.create(workorder=wo, action="started", actor=tech)
    print("Technician started work")

    # Tech completes
    wo.actual_end = timezone.now()
    wo.status = "completed"
    wo.technician_report = "Work completed successfully (E2E test)"
    wo.save()
    WorkOrderLog.objects.create(
        workorder=wo, action="completed", actor=tech, note=wo.technician_report
    )
    print("Technician completed work and saved report")

    # Engineer verifies
    wo.verified_by = engineer
    wo.verified_at = timezone.now()
    wo.verified_note = "Verified OK (E2E)"
    wo.status = "verified"
    wo.save()
    WorkOrderLog.objects.create(
        workorder=wo, action="verified", actor=engineer, note=wo.verified_note
    )
    print("Engineer verified work")

    # Print final state and logs
    wo.refresh_from_db()
    print("\n=== Final WorkOrder State ===")
    print(f"ID: {wo.id}")
    print(f"Title: {wo.title}")
    print(f"Status: {wo.status}")
    print(f"Accepted by: {wo.accepted_by}")
    print(f"Assigned to: {wo.assigned_to}")
    print(f"Actual start: {wo.actual_start}")
    print(f"Actual end: {wo.actual_end}")
    print(f"Technician report: {wo.technician_report}")
    print(f"Verified by: {wo.verified_by} at {wo.verified_at}")

    print("\n=== Logs (oldest -> newest) ===")
    for log in WorkOrderLog.objects.filter(workorder=wo).order_by("created_at"):
        actor = log.actor.username if log.actor else "System"
        print(f"[{log.created_at}] {log.action} by {actor} - {log.note}")

    print("\nE2E workflow test completed")


if __name__ == "__main__":
    main()
