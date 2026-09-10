
from workalendar.asia import Thailand

# Test workalendar
cal = Thailand()
holidays_2025 = cal.holidays(2025)

print(f"วันหยุดปี 2025 จาก workalendar API ({len(holidays_2025)} วัน):")
for date, name in holidays_2025:
    print(f"  {date.strftime('%Y-%m-%d')} - {name}")

print("\n" + "=" * 60)
print("เปรียบเทียบกับ JSON ของเรา:")

import json
import os

json_path = os.path.join("cmms", "data", "thai_holidays.json")
with open(json_path, "r", encoding="utf-8") as f:
    data = json.load(f)

our_holidays_2025 = data["years"].get("2025", [])
print(f"\nวันหยุดในไฟล์ JSON ({len(our_holidays_2025)} วัน):")
for h in our_holidays_2025:
    print(f"  {h['date']} - {h['name']}")

# Compare
print("\n" + "=" * 60)
print("การเปรียบเทียบ:")

api_dates = {str(date): name for date, name in holidays_2025}
json_dates = {h["date"]: h["name"] for h in our_holidays_2025}

# New in API
new_in_api = set(api_dates.keys()) - set(json_dates.keys())
if new_in_api:
    print(f"\n✓ วันหยุดใหม่จาก API ({len(new_in_api)} วัน):")
    for date in sorted(new_in_api):
        print(f"  {date} - {api_dates[date]}")

# Removed from API
removed_in_api = set(json_dates.keys()) - set(api_dates.keys())
if removed_in_api:
    print(f"\n✗ วันหยุดที่ถูกลบออก ({len(removed_in_api)} วัน):")
    for date in sorted(removed_in_api):
        print(f"  {date} - {json_dates[date]}")

# Updated
updated = []
for date in set(api_dates.keys()) & set(json_dates.keys()):
    if api_dates[date] != json_dates[date]:
        updated.append((date, json_dates[date], api_dates[date]))

if updated:
    print(f"\n↻ วันหยุดที่เปลี่ยนชื่อ ({len(updated)} วัน):")
    for date, old, new in sorted(updated):
        print(f"  {date}: '{old}' → '{new}'")

if not new_in_api and not removed_in_api and not updated:
    print("\n✓ ข้อมูลตรงกันทุกอย่าง!")
