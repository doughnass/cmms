// @ts-ignore: ignore missing dev dependency/type declarations during compile
import { test, expect, type Page } from '@playwright/test';

// This is a small smoke test: open the add technician page and ensure Select2 opens
// and results container appears when clicking the skills select.

test('skills select2 opens and shows results', async ({ page }: { page: Page }) => {
  // Adjust the URL to point to your local dev server if different
  await page.goto('http://localhost:8000/technicians/add/');

  // Wait for the skills select to be present
  const select = await page.locator('#id_skills_select');
  await expect(select).toBeVisible();

  // Click to focus / open Select2 dropdown (Select2 attaches to original element)
  await select.click();

  // The dropdown results container for Select2 has the class .select2-results
  const results = page.locator('.select2-results');
  await expect(results).toBeVisible({ timeout: 3000 });

  // If the results are empty, typing should trigger an AJAX call; type a short query
  await select.type('a');

  // Expect either some .select2-results__option elements or a 'no results' message
  const opts = page.locator('.select2-results__option');
  await expect(opts.first()).toBeVisible({ timeout: 3000 });
});
