"""
Cleanup script to remove E2E test data created by tools/e2e_test.py
Deletes users with username starting with 'e2e_' and WorkOrders with title starting with 'E2E Test WorkOrder'
Run with: python tools/e2e_cleanup.py
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

from cmms.models import WorkOrder

User = get_user_model()


def main():
    print("Starting E2E cleanup")
    # Delete WorkOrders created by E2E test
    wos = WorkOrder.objects.filter(title__startswith="E2E Test WorkOrder")
    count_wos = wos.count()
    for wo in wos:
        print(f"Deleting WorkOrder #{wo.id} - {wo.title}")
        wo.delete()

    # Delete users with username starting with e2e_
    users = User.objects.filter(username__startswith="e2e_")
    count_users = users.count()
    for u in users:
        print(f"Deleting user {u.username}")
        u.delete()

    print(f"Deleted {count_wos} WorkOrders and {count_users} users")


if __name__ == "__main__":
    main()
