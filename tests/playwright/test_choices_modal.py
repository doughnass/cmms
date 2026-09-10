"""
Playwright test (Python) — tests opening Choices Modal and selecting items.

Prerequisites:
- Install Playwright for Python:
    pip install playwright
    playwright install

Run dev server (if not running):
    python manage.py runserver

Run this test:
    pytest tests/playwright/test_choices_modal.py -q

Notes:
- This test assumes the app is available at http://localhost:8000
- Adjust URL below if your dev server runs on a different port or path
"""

from playwright.sync_api import sync_playwright
import time

BASE_URL = "http://localhost:8000"  # change if needed
CATEGORY_ADD_PATH = "/master/categories/add/"  # adjust if different


def test_open_choices_modal_and_select():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        # navigate to category add page
        page.goto(BASE_URL + CATEGORY_ADD_PATH)

        # wait for form to load (simple heuristic)
        page.wait_for_selector('form')

        # find first field_type select in the inline formset
        type_select = page.query_selector('[name$="-field_type"]')
        assert type_select, "No field_type select found"

        # set it to 'select' if possible
        try:
            # Try changing value via JS (in some formsets the select options may differ)
            page.select_option('[name$="-field_type"]', 'select')
        except Exception:
            # fallback: just click and set value via JS
            page.evaluate("(sel) => { sel.value = 'select'; sel.dispatchEvent(new Event('change')); }", type_select)

        # wait for load controls to appear
        page.wait_for_selector('.load-choices-controls', timeout=3000)

        # choose the first non-empty category in the dropdown
        cat_select = page.query_selector('.load-choices-from-category')
        assert cat_select, 'No category dropdown found'

        # try to pick the first available option value (skip empty)
        opts = page.query_selector_all('.load-choices-from-category option')
        chosen_val = None
        for opt in opts:
            val = opt.get_attribute('value')
            if val:
                chosen_val = val
                break
        assert chosen_val, 'No category option with value found to test'

        page.select_option('.load-choices-from-category', chosen_val)

        # wait a bit for data load or UI populate
        time.sleep(0.8)

        # click the modal open button (should become visible for select)
        open_btn = page.query_selector('.open-choices-modal-btn')
        assert open_btn, 'Open modal button not found'
        open_btn.click()

        # wait for modal
        page.wait_for_selector('#choicesModal.active', timeout=5000)

        # wait for table body rows
        page.wait_for_selector('#choicesModalTableBody tr', timeout=5000)

        # click first row checkbox
        first_cb = page.query_selector('#choicesModalTableBody input.modal-row-cb')
        assert first_cb, 'No checkbox found in modal rows'
        first_cb.check()

        # confirm
        page.click('#confirmChoicesModal')

        # modal should close
        page.wait_for_selector('#choicesModal', state='hidden', timeout=3000)

        # verify the hidden choices input now contains JSON
        choices_input = page.query_selector('.choices-wrapper textarea, .choices-wrapper input[type="text"], .choices-wrapper input[type="hidden"]')
        assert choices_input, 'Choices input not found after confirm'
        val = choices_input.input_value().strip()
        assert val.startswith('[') and val.endswith(']'), 'Choices input does not contain JSON array: %s' % val

        # cleanup
        context.close()
        browser.close()
