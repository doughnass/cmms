"""
Playwright smoke test (Python - sync API)

Improved behavior:
- Read BASE from env var (BASE) or default to http://localhost:8000
- Use playwright waiting primitives instead of time.sleep
- Handle AJAX-loaded picker tree and fallback refresh
- Print clear diagnostic output for CI or local runs

Usage:
  pip install playwright
  python -m playwright install
  BASE=http://localhost:8000 python tools/playwright/test_parent_picker.py
"""

import os

from playwright.sync_api import TimeoutError as PWTimeout
from playwright.sync_api import sync_playwright

BASE = os.environ.get("BASE", "http://localhost:8000")


def run():
    results = {"ok": False, "messages": []}
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            url = BASE.rstrip("/") + "/master/manage/"
            results["messages"].append(f"Navigating to {url}")
            page.goto(url, wait_until="domcontentloaded", timeout=10000)

            # wait for the tree or a hint that category must be chosen
            try:
                page.wait_for_selector("#master-tree, .list-group", timeout=5000)
            except PWTimeout:
                results["messages"].append(
                    "master-tree not found (page may require category selection)"
                )

            # try to find a visible add-child button
            add_btn = page.query_selector(".btn-add-child")
            # If no add button found, maybe a category must be selected first; try clicking first category link
            if not add_btn:
                # try to click a category in the left list-group
                cat = page.query_selector('.list-group a[href*="/master/manage/"]')
                if cat:
                    try:
                        cat.click()
                        page.wait_for_load_state("domcontentloaded", timeout=5000)
                        page.wait_for_timeout(300)
                    except Exception:
                        pass
                # try expanding first toggle to reveal action buttons as a fallback
                toggle = page.query_selector(".node-toggle, .master-node-toggle")
                if toggle:
                    try:
                        toggle.click()
                        page.wait_for_timeout(400)
                    except Exception:
                        pass
                add_btn = page.query_selector(".btn-add-child")

            if not add_btn:
                results["messages"].append(
                    "No .btn-add-child found; ensure tree has nodes and you are in a category view"
                )
                print(results)
                return

            add_btn.click()

            # wait for modal to show
            try:
                page.wait_for_selector(
                    "#masterModal.show, #masterModal .modal-content", timeout=7000
                )
            except PWTimeout:
                results["messages"].append("masterModal did not appear")
                print(results)
                return

            # open parent picker
            try:
                page.click("#mi-change-parent-btn")
            except Exception:
                results["messages"].append("mi-change-parent-btn not clickable")
                print(results)
                return

            # wait for picker modal to open or tree to be populated
            try:
                page.wait_for_selector(
                    "#parentPickerModal.show, #parent-picker-tree .picker-node, #parent-picker-tree .picker-node-wrapper",
                    timeout=7000,
                )
            except PWTimeout:
                # fallback: try clicking refresh button inside picker if present
                results["messages"].append(
                    "picker did not show immediately; attempting refresh"
                )
                try:
                    page.click("#parent-picker-refresh")
                    page.wait_for_selector(
                        "#parent-picker-tree .picker-node, #parent-picker-tree .picker-node-wrapper",
                        timeout=5000,
                    )
                except Exception:
                    results["messages"].append("picker nodes not found after refresh")
                    print(results)
                    return

            # select first available node (support different DOM structures)
            node = page.query_selector(
                "#parent-picker-tree .picker-node, #parent-picker-tree .picker-node-wrapper, #parent-picker-tree .picker-node-row, #parent-picker-tree .picker-node"
            )
            if not node:
                results["messages"].append("No picker nodes found; picker may be empty")
                print(results)
                return

            # click node and wait for preview text to update
            node.click()
            try:
                preview = page.wait_for_selector("#parent-picker-preview", timeout=3000)
                pv_text = preview.inner_text().strip()
                results["messages"].append("Preview text: " + (pv_text or "(empty)"))
            except Exception:
                results["messages"].append("No preview element or preview not updated")

            # wait for select button to be enabled
            try:
                select_btn = page.wait_for_selector(
                    "#parent-picker-select", timeout=3000
                )
                # poll until enabled or timeout
                enabled = False
                for _ in range(10):
                    if not select_btn.is_enabled():
                        page.wait_for_timeout(200)
                        continue
                    enabled = True
                    break
                if not enabled:
                    results["messages"].append(
                        "Select button disabled after node selection"
                    )
                    print(results)
                    return
                select_btn.click()
            except Exception:
                results["messages"].append(
                    "parent-picker-select missing or not clickable"
                )
                print(results)
                return

            # check hidden input updated
            try:
                hid = page.wait_for_selector("#mi-parent", timeout=3000)
                hid_val = hid.get_attribute("value") or ""
                results["messages"].append(
                    "Hidden parent id: " + (hid_val or "(empty)")
                )
            except Exception:
                results["messages"].append(
                    "Hidden input #mi-parent not found or not updated"
                )

            results["ok"] = True
            print(results)

        finally:
            try:
                browser.close()
            except Exception:
                pass


if __name__ == "__main__":
    run()
