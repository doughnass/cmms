import os
import sys
import time

import django

# Ensure project root is on sys.path
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cmms_project.settings")
django.setup()

from django.contrib.auth import get_user_model
from django.test import Client

User = get_user_model()


def ensure_dev_user():
    u, created = User.objects.get_or_create(
        username="devadmin", defaults={"email": "devadmin@example.com"}
    )
    if created:
        u.set_password("devpass")
        u.is_staff = True
        u.is_superuser = True
        u.save()
        print("Created devadmin")
    else:
        if not u.is_staff:
            u.is_staff = True
            u.save()
        print("Found devadmin")
    return u


def run():
    # set HTTP_HOST to a value in ALLOWED_HOSTS (or localhost) so CommonMiddleware doesn't reject request
    c = Client(HTTP_HOST="127.0.0.1")
    user = ensure_dev_user()
    # force login
    c.force_login(user)

    cat = f"e2e_test_cat_{int(time.time())}"
    print("Using category:", cat)

    # Create parent
    parent_payload = {
        "category": cat,
        "code": "p1",
        "label": "Parent Node",
        "description": "E2E parent",
        "active": "true",
        "order": "10",
    }
    r = c.post("/master/api/create/", parent_payload)
    print("Create parent status:", r.status_code, r.content.decode())
    pj = r.json()
    if not pj.get("ok"):
        print("Parent create failed, abort")
        return
    parent_id = pj.get("id")

    # Create child
    child_payload = {
        "category": cat,
        "code": "c1",
        "label": "Child Node",
        "description": "E2E child",
        "active": "true",
        "order": "20",
        "parent_id": str(parent_id),
    }
    r2 = c.post("/master/api/create/", child_payload)
    print("Create child status:", r2.status_code, r2.content.decode())
    cj = r2.json()
    if not cj.get("ok"):
        print("Child create failed, cleaning parent and exiting")
        c.post(f"/master/api/delete/{parent_id}/")
        return
    child_id = cj.get("id")

    # Get child
    r3 = c.get(f"/master/api/get/{child_id}/")
    print("Get child:", r3.status_code, r3.content.decode())

    # Update child label
    up_payload = {
        "label": "Child Node UPDATED",
        "category": cat,
        "code": "c1",
        "order": "25",
    }
    r4 = c.post(f"/master/api/update/{child_id}/", up_payload)
    print("Update child:", r4.status_code, r4.content.decode())

    # Verify update
    r5 = c.get(f"/master/api/get/{child_id}/")
    print("Get child after update:", r5.status_code, r5.content.decode())

    # Delete child
    r6 = c.post(f"/master/api/delete/{child_id}/")
    print("Delete child:", r6.status_code, r6.content.decode())

    # Delete parent
    r7 = c.post(f"/master/api/delete/{parent_id}/")
    print("Delete parent:", r7.status_code, r7.content.decode())

    print("E2E CRUD test finished")


if __name__ == "__main__":
    run()
