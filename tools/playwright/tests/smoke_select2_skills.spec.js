const { test, expect } = require('@playwright/test');

// Basic smoke test (JS) to avoid TypeScript setup in repo environment.
// Ensure dev server is running at PLAYWRIGHT_BASE or http://127.0.0.1:8000
const BASE = process.env.PLAYWRIGHT_BASE || 'http://127.0.0.1:8000';

test('skills select2 opens and shows results', async ({ page }) => {
  await page.goto(`${BASE}/maintenance/technicians/add/`);

  const select = page.locator('#id_skills_select');
  await expect(select).toBeVisible();

  await select.click();

  const results = page.locator('.select2-results');
  await expect(results).toBeVisible({ timeout: 3000 });

  // attempt a query to trigger AJAX
  await select.type('a');
  const opts = page.locator('.select2-results__option');
  await expect(opts.first()).toBeVisible({ timeout: 3000 });
});
