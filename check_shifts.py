import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cmms_project.settings")
django.setup()

from cmms.models import ShiftSchedule

schedules = ShiftSchedule.objects.all().order_by("date")
print(f"📊 Total schedules: {schedules.count()}")
print()

if schedules.count() > 0:
    print("📋 Schedules by month:")
    from collections import defaultdict

    by_month = defaultdict(list)

    for s in schedules:
        month_key = f"{s.date.year}-{s.date.month:02d}"
        by_month[month_key].append(s)

    for month_key in sorted(by_month.keys()):
        print(f"\n  📅 {month_key}: {len(by_month[month_key])} schedules")
        for s in by_month[month_key][:5]:
            print(f"      - {s.date} ({s.shift}): {s.technician.name}")
        if len(by_month[month_key]) > 5:
            print(f"      ... และอีก {len(by_month[month_key]) - 5} รายการ")
else:
    print("❌ ไม่มีข้อมูล ShiftSchedule ในฐานข้อมูล!")
