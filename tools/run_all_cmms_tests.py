"""Temp helper: enumerate cmms/tests test_*.py modules and invoke manage.py test with explicit labels."""

import os
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEST_DIR = os.path.join(ROOT, "cmms", "tests")
mods = []
for fn in os.listdir(TEST_DIR):
    if fn.startswith("test_") and fn.endswith(".py"):
        name = fn[:-3]
        mods.append(f"cmms.tests.{name}")
if not mods:
    print("No test modules found")
    raise SystemExit(1)
cmd = ["python", os.path.join(ROOT, "manage.py"), "test"] + mods
print("Running:", " ".join(cmd))
res = subprocess.run(cmd)
raise SystemExit(res.returncode)
