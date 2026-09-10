#!/usr/bin/env python
"""Debug helper: print MasterItem(workorder_type) and KPI type arrays."""
import os
import sys
import json

# Ensure project root is on sys.path so Django settings module can be imported
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cmms_project.settings')
import django
django.setup()

from cmms.models import MasterItem
from cmms.views_reports import calculate_kpis, get_date_range

start, end = get_date_range('month')
kpis = calculate_kpis(start, end)

print('MASTER_TYPES:')
for m in MasterItem.objects.filter(category='workorder_type', active=True).order_by('order', 'label'):
    print(f"{m.id}\tcode={m.code!r}\tlabel={m.label!r}")

print('\nKPI JSON ARRAYS:')
print('type_labels_json:', kpis.get('type_labels_json'))
print('type_codes_json :', kpis.get('type_codes_json'))
print('type_counts_json:', kpis.get('type_counts_json'))

# Print parsed arrays
try:
    labels = json.loads(kpis.get('type_labels_json') or '[]')
    codes = json.loads(kpis.get('type_codes_json') or '[]')
    counts = json.loads(kpis.get('type_counts_json') or '[]')
    print('\nPARSED:')
    for lab, cod, cnt in zip(labels, codes, counts):
        print('->', lab, cod, cnt)
except Exception as e:
    print('Failed to parse JSON arrays:', e)

print('\nLEGACY COUNTS:')
print('maintenance_count:', kpis.get('maintenance_count'))
print('repair_count     :', kpis.get('repair_count'))
print('calibration_count:', kpis.get('calibration_count'))
print('other_count      :', kpis.get('other_count'))
print('untyped_count    :', kpis.get('untyped_count'))
