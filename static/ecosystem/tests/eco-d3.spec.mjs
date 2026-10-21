import { test, expect } from '@playwright/test';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const OUT = path.join(__dirname, '..', 'screenshots-d3');
const BASE = (process.env.ECO_BASE || 'http://127.0.0.1:8797/ecosystem/').replace(/\/?$/, '/');
function ecoQuery(qs) {
  return BASE.includes('?') ? `${BASE}&${qs}` : `${BASE}?${qs}`;
}

test.describe('ecosystem D3', () => {
  test('loads without console errors', async ({ page }) => {
    const errors = [];
    page.on('console', (msg) => {
      if (msg.type() !== 'error') return;
      const text = msg.text();
      if (/Failed to load resource.*404/.test(text)) return;
      errors.push(text);
    });
    page.on('pageerror', (err) => {
      const s = String(err);
      if (/Sigma: Container has no width/.test(s)) return;
      errors.push(s);
    });
    await page.goto(ecoQuery('preview=1&state=overview'), { waitUntil: 'domcontentloaded', timeout: 60000 });
    await expect(page.locator('#stat-actors')).not.toHaveText('—', { timeout: 60000 });
    await page.waitForSelector('body[data-eco-ready="1"]', { timeout: 15000 }).catch(() => {});
    expect(errors, errors.join('\n')).toEqual([]);
  });

  test('screenshots', async ({ page }) => {
    const shots = [
      { name: 'overview', url: ecoQuery('preview=1&state=overview') },
      { name: 'actor-selected', url: ecoQuery('preview=1&state=selected&actor=pe-emprende-up-climatech-rein-hub-peru') },
      { name: 'ego-2hop', url: ecoQuery('preview=1&state=ego&depth=2&actor=pe-emprende-up-climatech-rein-hub-peru') },
      { name: 'filters', url: ecoQuery('preview=1&state=filters&country=PE&cats=accelerator,government,funder') },
      { name: 'mobile-selected', url: ecoQuery('preview=1&state=selected&mobile=1&actor=pe-emprende-up-climatech-rein-hub-peru') },
    ];
    for (const s of shots) {
      await page.goto(s.url, { waitUntil: 'domcontentloaded', timeout: 60000 });
      await expect(page.locator('#stat-actors')).not.toHaveText('—', { timeout: 60000 });
      await page.waitForTimeout(800);
      await page.screenshot({ path: path.join(OUT, `${s.name}.png`), fullPage: true });
    }
  });
});
