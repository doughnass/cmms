import os
import django
import sys

# Ensure DJANGO_SETTINGS_MODULE points to your project settings
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cmms_project.settings')
django.setup()

from cmms.models import MaintenanceTaskDuration

defaults = [('maintenance', 1.0), ('calibration', 1.5), ('repair', 2.0)]
for t, h in defaults:
    obj, created = MaintenanceTaskDuration.objects.update_or_create(
        task_type=t,
        defaults={'hours': h}
    )
    print(f"Set {t} -> {h} (created={created})")

print('Seeding complete')
