import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cmms_project.settings")
import django

django.setup()
from django.contrib.auth import get_user_model
from django.test import Client

User = get_user_model()

u, created = User.objects.get_or_create(
    username="devadmin", defaults={"email": "devadmin@example.com"}
)
if created:
    u.set_password("devpass")
    u.is_staff = True
    u.is_superuser = True
    u.save()
else:
    if not u.is_staff:
        u.is_staff = True
        u.save()

c = Client(HTTP_HOST="127.0.0.1")
c.force_login(u)
from cmms.models import MasterItem

cats = list(MasterItem.objects.values_list("category", flat=True).distinct())
cat = cats[0] if cats else ""
url = "/master/manage/" + (cat or "")
print("GET", url)
r = c.get(url)
print("status", r.status_code)
html = r.content.decode("utf-8", errors="ignore")
print("has modal?", "masterModal" in html)
print("has csrf?", "csrfmiddlewaretoken" in html)
print("has import link?", "master_import_excel" in html)
