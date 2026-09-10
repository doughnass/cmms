Playwright smoke test for Master parent-picker

Requirements:
- Python 3.8+
- Install packages:

pip install playwright pytest
playwright install

Run dev server (Django):

# from project root
python manage.py runserver

Run the smoke test:

python tools/playwright/test_parent_picker.py

Notes:
- The script assumes the manage page is at /master/manage/ and that the tree has at least one node with .btn-add-child
- If your dev server runs on a different port, update BASE in the script
- This is a minimal smoke test; for CI integration use pytest-playwright or Playwright test runner.