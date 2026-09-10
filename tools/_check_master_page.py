import os
import sys

import django

# Ensure project root is on sys.path so Django can import settings
THIS_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(THIS_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cmms_project.settings")
django.setup()

from django.test import Client


def main():
    c = Client()
    # Test client uses 'testserver' by default which may be disallowed; provide HTTP_HOST
    # First fetch the general master list
    r = c.get("/master/", HTTP_HOST="127.0.0.1")
    print("status", r.status_code)
    html = r.content.decode("utf-8")
    print("has_expand_all=", "Expand all" in html)

    # If there are categories, request the first category-specific tree view
    from cmms.models import MasterItem

    cats = list(MasterItem.objects.values_list("category", flat=True).distinct())
    if cats:
        cat = cats[0]
        print("testing category:", cat)
        r2 = c.get(f"/master/category/{cat}/", HTTP_HOST="127.0.0.1")
        print("status(category)", r2.status_code)
        html2 = r2.content.decode("utf-8")
        print("has_toggle=", "master-node-toggle" in html2)
        print("snippet category:\n", html2[:1200])
    else:
        print("no categories found")


if __name__ == "__main__":
    main()
