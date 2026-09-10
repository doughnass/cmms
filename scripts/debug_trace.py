#!/usr/bin/env python
"""Step-by-step trace for type-counting logic."""
import os, sys, json
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cmms_project.settings')
import django; django.setup()

from django.db.models import Q
from cmms.models import WorkOrder, MasterItem
from cmms.views_reports import get_date_range, _TITLE_TYPE_Q

start, end = get_date_range('month')
print('Range:', start, '-', end)

work_orders = WorkOrder.objects.filter(reported_at__date__range=[start, end])
print('WOs in range:', work_orders.count())
for w in work_orders:
    print(f'  WO#{w.id} type={w.workorder_type!r} m2m={list(w.workorder_types.all())} title={w.title!r}')

master_types = list(MasterItem.objects.filter(category='workorder_type', active=True).order_by('order', 'label'))
master_id_by_code = {m.code: m.id for m in master_types if m.code}

print('\n--- M2M counts ---')
counts_by_master = {}
for m in master_types:
    c = work_orders.filter(workorder_types__id=m.id).distinct().count()
    counts_by_master[m.id] = c
    if c:
        print(f'  {m.label} ({m.code}): {c}')

no_m2m_qs = work_orders.filter(workorder_types__isnull=True)
print(f'\nno_m2m count: {no_m2m_qs.count()}')

print('\n--- Charfield loop (skip other) ---')
for code, mid in master_id_by_code.items():
    if code == 'other':
        continue
    c = no_m2m_qs.filter(workorder_type=code).count()
    if c:
        counts_by_master[mid] += c
        print(f'  {code}: {c}')

unfiled_qs = no_m2m_qs.filter(workorder_type='other')
print(f'\nunfiled count: {unfiled_qs.count()}')
for w in unfiled_qs:
    print(f'  WO#{w.id} title={w.title!r}')

assigned_ids = set()
print('\n--- Title keyword loop ---')
for code, q_expr in _TITLE_TYPE_Q.items():
    ids = list(unfiled_qs.filter(q_expr).values_list('id', flat=True))
    if ids:
        print(f'  {code}: matched ids {ids}')
        if code in master_id_by_code:
            counts_by_master[master_id_by_code[code]] += len(ids)
        assigned_ids.update(ids)
print(f'  assigned_ids after keyword loop: {assigned_ids}')

remaining_qs = unfiled_qs.exclude(id__in=assigned_ids)
print(f'\nremaining after keywords: {remaining_qs.count()}')
print('\n--- Label loop ---')
for m in master_types:
    label = (m.label or '').strip()
    if not label:
        continue
    ids = list(remaining_qs.filter(title__icontains=label).values_list('id', flat=True))
    if ids:
        counts_by_master[m.id] += len(ids)
        assigned_ids.update(ids)
        print(f'  {m.label} ({m.code}): matched ids {ids}')

untyped = unfiled_qs.exclude(id__in=assigned_ids).count()
print(f'\nuntyped: {untyped}')

print('\n--- Final counts ---')
for m in master_types:
    c = counts_by_master.get(m.id, 0)
    print(f'  {m.label} ({m.code}): {c}')
