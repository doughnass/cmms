"""
Update equipment status master data with new 3-group structure:
1. Operational Status (ready=green, not_ready=red)
2. Maintenance Status (PM/CAL with icons)
3. Warranty Status (with icons)
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cmms_project.settings')
django.setup()

from cmms.models import MasterItem

# Define status structure by groups
STATUS_DEFINITIONS = [
    # === กลุ่มที่ 1: สถานะการใช้งาน (Operational Status) ===
    {
        'category': 'equipment_status',
        'code': 'ready',
        'label': 'พร้อมใช้งาน',
        'order': 10,
        'active': True,
        'meta': {
            'group': 'operational',
            'color': 'success',  # เขียว
            'icon': 'check-circle-fill',
            'priority': 0,
            'description': 'เครื่องมือพร้อมใช้งานปกติ'
        }
    },
    {
        'category': 'equipment_status',
        'code': 'not_ready',
        'label': 'ไม่พร้อมใช้งาน',
        'order': 11,
        'active': True,
        'meta': {
            'group': 'operational',
            'color': 'danger',  # แดง
            'icon': 'x-circle-fill',
            'priority': 100,
            'description': 'เครื่องมือไม่พร้อมใช้งาน/ชำรุด'
        }
    },
    {
        'category': 'equipment_status',
        'code': 'under_repair',
        'label': 'อยู่ระหว่างซ่อม',
        'order': 12,
        'active': True,
        'meta': {
            'group': 'operational',
            'color': 'warning',  # เหลือง
            'icon': 'tools',
            'priority': 50,
            'description': 'เครื่องมืออยู่ระหว่างการซ่อมแซม'
        }
    },
    
    # === กลุ่มที่ 2: สถานะการบำรุงรักษา (Maintenance Status) ===
    {
        'category': 'equipment_status',
        'code': 'pm_overdue',
        'label': 'PM เกินกำหนด',
        'order': 20,
        'active': True,
        'meta': {
            'group': 'maintenance',
            'color': 'danger',
            'icon': 'exclamation-triangle-fill',
            'priority': 10,
            'description': 'การบำรุงรักษาตามแผนเกินกำหนด'
        }
    },
    {
        'category': 'equipment_status',
        'code': 'pm_due_soon',
        'label': 'PM ใกล้ครบกำหนด',
        'order': 21,
        'active': True,
        'meta': {
            'group': 'maintenance',
            'color': 'warning',
            'icon': 'clock-fill',
            'priority': 5,
            'description': 'การบำรุงรักษาตามแผนใกล้ครบกำหนด (≤7 วัน)'
        }
    },
    {
        'category': 'equipment_status',
        'code': 'pm_ok',
        'label': 'PM ปกติ',
        'order': 22,
        'active': True,
        'meta': {
            'group': 'maintenance',
            'color': 'success',
            'icon': 'check-circle-fill',
            'priority': 0,
            'description': 'การบำรุงรักษาตามแผนอยู่ในเกณฑ์ปกติ'
        }
    },
    {
        'category': 'equipment_status',
        'code': 'cal_overdue',
        'label': 'CAL เกินกำหนด',
        'order': 23,
        'active': True,
        'meta': {
            'group': 'maintenance',
            'color': 'danger',
            'icon': 'exclamation-triangle-fill',
            'priority': 10,
            'description': 'การสอบเทียบเกินกำหนด'
        }
    },
    {
        'category': 'equipment_status',
        'code': 'cal_due_soon',
        'label': 'CAL ใกล้ครบกำหนด',
        'order': 24,
        'active': True,
        'meta': {
            'group': 'maintenance',
            'color': 'warning',
            'icon': 'clock-fill',
            'priority': 5,
            'description': 'การสอบเทียบใกล้ครบกำหนด (≤14 วัน)'
        }
    },
    {
        'category': 'equipment_status',
        'code': 'cal_ok',
        'label': 'CAL ปกติ',
        'order': 25,
        'active': True,
        'meta': {
            'group': 'maintenance',
            'color': 'success',
            'icon': 'check-circle-fill',
            'priority': 0,
            'description': 'การสอบเทียบอยู่ในเกณฑ์ปกติ'
        }
    },
    
    # === กลุ่มที่ 3: สถานะการรับประกัน (Warranty Status) ===
    {
        'category': 'equipment_status',
        'code': 'warranty_expired',
        'label': 'หมดประกัน',
        'order': 30,
        'active': True,
        'meta': {
            'group': 'warranty',
            'color': 'secondary',
            'icon': 'shield-x',
            'priority': 1,
            'description': 'สัญญาการรับประกันหมดอายุแล้ว'
        }
    },
    {
        'category': 'equipment_status',
        'code': 'warranty_expiring',
        'label': 'ใกล้หมดประกัน',
        'order': 31,
        'active': True,
        'meta': {
            'group': 'warranty',
            'color': 'info',
            'icon': 'shield-exclamation',
            'priority': 2,
            'description': 'สัญญาการรับประกันใกล้หมดอายุ (≤30 วัน)'
        }
    },
    {
        'category': 'equipment_status',
        'code': 'warranty_ok',
        'label': 'อยู่ในประกัน',
        'order': 32,
        'active': True,
        'meta': {
            'group': 'warranty',
            'color': 'success',
            'icon': 'shield-check',
            'priority': 0,
            'description': 'สัญญาการรับประกันยังไม่หมดอายุ'
        }
    },
]

def update_status_master():
    """Update or create equipment status master data"""
    created_count = 0
    updated_count = 0
    
    print("=== Updating Equipment Status Master Data ===\n")
    
    for status_def in STATUS_DEFINITIONS:
        code = status_def['code']
        category = status_def['category']
        
        obj, created = MasterItem.objects.update_or_create(
            category=category,
            code=code,
            defaults={
                'label': status_def['label'],
                'order': status_def['order'],
                'active': status_def['active'],
                'meta': status_def['meta']
            }
        )
        
        if created:
            created_count += 1
            print(f"✅ Created: [{code}] {status_def['label']}")
            print(f"   Group: {status_def['meta']['group']}, Color: {status_def['meta']['color']}")
        else:
            updated_count += 1
            print(f"🔄 Updated: [{code}] {status_def['label']}")
            print(f"   Group: {status_def['meta']['group']}, Color: {status_def['meta']['color']}")
    
    print(f"\n{'='*50}")
    print(f"Summary: {created_count} created, {updated_count} updated, {created_count + updated_count} total")
    print(f"{'='*50}\n")
    
    # Display by groups
    print("=== Status by Groups ===\n")
    
    groups = ['operational', 'maintenance', 'warranty']
    group_labels = {
        'operational': 'กลุ่มที่ 1: สถานะการใช้งาน',
        'maintenance': 'กลุ่มที่ 2: สถานะการบำรุงรักษา',
        'warranty': 'กลุ่มที่ 3: สถานะการรับประกัน'
    }
    
    for group in groups:
        print(f"\n📁 {group_labels[group]}")
        print("-" * 50)
        
        items = MasterItem.objects.filter(
            category='equipment_status',
            active=True,
            meta__group=group
        ).order_by('order')
        
        for item in items:
            meta = item.meta if item.meta else {}
            print(f"  • [{item.code}] {item.label}")
            print(f"    Color: {meta.get('color', '-')}, Icon: {meta.get('icon', '-')}, Priority: {meta.get('priority', '-')}")

if __name__ == '__main__':
    update_status_master()
