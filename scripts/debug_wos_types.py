#!/usr/bin/env python
"""Debug helper: list WorkOrders and their type fields/M2M for inspection."""
import os
import sys
import json

# Ensure project root is on sys.path
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cmms_project.settings')
import django
django.setup()

from cmms.views_reports import get_date_range
from cmms.models import WorkOrder

start, end = get_date_range('month')
print('Date range:', start, '->', end)

wos = WorkOrder.objects.filter(reported_at__date__range=[start, end]).prefetch_related('workorder_types')
print('WorkOrders found:', wos.count())
for wo in wos.order_by('-reported_at')[:200]:
    m2m = [(m.id, m.code, m.label) for m in wo.workorder_types.all()]
    print(f"WO#{wo.id}\treported:{wo.reported_at.date()}\tstatus:{wo.status}\tchar:{wo.workorder_type!r}\tm2m:{m2m}\ttitle:{wo.title}")
