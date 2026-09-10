"""
Quick test for multi-account feature.
Creates two users (test_a, test_b), logs in as test_a, adds test_b as alternate, then switches to test_b.
"""

import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cmms_project.settings")
import django

django.setup()

from django.contrib.auth import get_user_model
from django.test import Client

User = get_user_model()

u1, created = User.objects.get_or_create(
    username="test_a", defaults={"email": "a@example.com"}
)
if created:
    u1.set_password("pass_a")
    u1.save()

u2, created = User.objects.get_or_create(
    username="test_b", defaults={"email": "b@example.com"}
)
if created:
    u2.set_password("pass_b")
    u2.save()

c = Client()
logged = c.login(username="test_a", password="pass_a")
print("logged as test_a:", logged)

# add account: post credentials for test_b
resp = c.post("/accounts/add/", {"username": "test_b", "password": "pass_b"})
print("/accounts/add/ status", resp.status_code, resp.content)

# inspect session alt_accounts
print("session alt_accounts:", c.session.get("alt_accounts"))

# now switch to test_b
resp2 = c.post("/accounts/switch/", {"username": "test_b"})
print("/accounts/switch/ status", resp2.status_code, resp2.content)
# after switch, check auth user id in session
print("session _auth_user_id:", c.session.get("_auth_user_id"))

# final check: try profile page
r = c.get("/profile/")
print("/profile/ status", r.status_code)

print("done")
