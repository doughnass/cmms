#!/usr/bin/env python
import sys
from datetime import date
import django
import os

# Ensure project root is on path
SCRIPT_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cmms_project.settings')
django.setup()

from cmms.models import MaintenanceAppointment, MaintenanceTaskDuration

# Change this date as needed
D = date(2025, 12, 3)

qs = MaintenanceAppointment.objects.filter(scheduled_date=D).select_related('equipment')

# Load defaults
defaults_qs = MaintenanceTaskDuration.objects.all()
defaults = {m.task_type: float(m.hours) for m in defaults_qs}
default_maintenance = defaults.get('maintenance', 1.0)

total = 0.0
for a in qs:
    e = a.equipment
    est = e.estimated_hours
    if est is None:
        est = default_maintenance
    total += float(est)

print(f"date={D}, appointments={qs.count()}, total_hours={total:.2f}")
for a in qs:
    e = a.equipment
    est = e.estimated_hours if e.estimated_hours is not None else default_maintenance
    name = (e.equipment_name_EN or e.equipment_name_TH or '').strip()
    print(f"- appointment_id={a.id} equipment_id={e.equipment_id} name='{name}' est_hours={float(est)}")
