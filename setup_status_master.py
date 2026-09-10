#!/usr/bin/env python
"""Setup equipment_status master data"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cmms_project.settings')
django.setup()

from cmms.models import MasterItem

statuses = [
    {
        'code': 'normal',
        'label': 'ปกติ',
        'meta': {
            'color': 'success',
            'icon': 'check-circle-fill',
            'priority': 0
        }
    },
    {
        'code': 'pm_due_soon',
        'label': 'PM ใกล้ครบกำหนด',
        'meta': {
            'color': 'warning',
            'icon': 'clock-fill',
            'priority': 5
        }
    },
    {
        'code': 'pm_overdue',
        'label': 'PM เกินกำหนด',
        'meta': {
            'color': 'danger',
            'icon': 'exclamation-triangle-fill',
            'priority': 10
        }
    },
    {
        'code': 'cal_due_soon',
        'label': 'CAL ใกล้ครบกำหนด',
        'meta': {
            'color': 'warning',
            'icon': 'clock-fill',
            'priority': 5
        }
    },
    {
        'code': 'cal_overdue',
        'label': 'CAL เกินกำหนด',
        'meta': {
            'color': 'danger',
            'icon': 'exclamation-triangle-fill',
            'priority': 10
        }
    },
    {
        'code': 'warranty_expiring',
        'label': 'ประกันใกล้หมด',
        'meta': {
            'color': 'info',
            'icon': 'shield-exclamation',
            'priority': 2
        }
    },
    {
        'code': 'warranty_expired',
        'label': 'หมดประกัน',
        'meta': {
            'color': 'secondary',
            'icon': 'shield-x',
            'priority': 1
        }
    },
]

created = 0
updated = 0

for i, status_data in enumerate(statuses):
    obj, is_new = MasterItem.objects.update_or_create(
        category='equipment_status',
        code=status_data['code'],
        defaults={
            'label': status_data['label'],
            'meta': status_data['meta'],
            'active': True,
            'order': i * 10
        }
    )
    if is_new:
        created += 1
        print(f"✅ Created: {status_data['code']} - {status_data['label']}")
    else:
        updated += 1
        print(f"🔄 Updated: {status_data['code']} - {status_data['label']}")

print(f"\n📊 Summary: {created} created, {updated} updated, {len(statuses)} total")
