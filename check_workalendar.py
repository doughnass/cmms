"""
Check what's available in workalendar.asia
"""

import workalendar.asia

print("Available classes in workalendar.asia:")
print(dir(workalendar.asia))

print("\n" + "=" * 60)
print("Trying to find Thailand-related classes:")

for name in dir(workalendar.asia):
    if "thai" in name.lower():
        print(f"  - {name}")
        obj = getattr(workalendar.asia, name)
        print(f"    Type: {type(obj)}")
        if hasattr(obj, "__bases__"):
            print(f"    Bases: {obj.__bases__}")

# Try common variations
variations = [
    "Thailand",
    "ThailandCalendar",
    "Thai",
    "ThaiCalendar",
]

print("\n" + "=" * 60)
print("Testing class name variations:")
for var in variations:
    try:
        cls = getattr(workalendar.asia, var, None)
        if cls:
            print(f"  ✓ Found: {var}")
            cal = cls()
            holidays = cal.holidays(2025)
            print(f"    Holidays 2025: {len(holidays)} days")
        else:
            print(f"  ✗ Not found: {var}")
    except Exception as e:
        print(f"  ✗ Error with {var}: {e}")
