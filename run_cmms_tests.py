"""Run cmms app tests by enumerating test modules and invoking manage.py test with explicit labels.

This avoids unittest discovery issues where a 'tests' package can be imported as a top-level module
and cause ImportError: 'tests' module incorrectly imported ...

Usage:
    python run_cmms_tests.py

"""

import os
import subprocess

ROOT = os.path.dirname(os.path.abspath(__file__))
CMMS_TEST_DIR = os.path.join(ROOT, "cmms", "tests")

mods = []
for fn in os.listdir(CMMS_TEST_DIR):
    if fn.startswith("test_") and fn.endswith(".py"):
        name = fn[:-3]
        mods.append(f"cmms.tests.{name}")

if not mods:
    print("No test modules found in cmms/tests")
    raise SystemExit(1)

cmd = ["python", os.path.join(ROOT, "manage.py"), "test"] + mods
print("Running:", " ".join(cmd))
res = subprocess.run(cmd)
raise SystemExit(res.returncode)
