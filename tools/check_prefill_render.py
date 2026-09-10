"""Create demo SRs and render workorder_create page for one SR; print small HTML snippets to verify prefill.
Run: python tools\check_prefill_render.py
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
from django.test import RequestFactory

from cmms.models import ServiceRequest
from cmms.views import workorder_create

User = get_user_model()
user = User.objects.filter(is_superuser=True).first()
# create demo SRs
srs = []
for i in range(3):
    s = ServiceRequest.objects.create(
        title=f"Demo SR #{i+1}", description=f"Description {i+1}"
    )
    srs.append(s)
print("Created SR ids:", [s.id for s in srs])
# render create page for second SR
rf = RequestFactory()
req = rf.get(f"/workorders/create?from_sr={srs[1].id}")
req.user = user
resp = workorder_create(req)
html = resp.content.decode("utf-8")
# find banner
start = html.find("กำลังสร้างใบงานจากคำขอรับบริการ")
snippet = html[start : start + 400] if start != -1 else "(banner not found)"
print("\n--- Banner snippet ---\n")
print(snippet)
# check title field value
title_idx = html.find('name="title"')
chunk = (
    html[title_idx : title_idx + 400] if title_idx != -1 else "(title input not found)"
)
print("\n--- Title input snippet ---\n")
print(chunk)
