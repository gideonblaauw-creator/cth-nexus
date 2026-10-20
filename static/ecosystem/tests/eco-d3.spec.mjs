import { test, expect } from '@playwright/test';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const OUT = path.join(__dirname, '..', 'screenshots-d3');
const BASE = process.env.ECO_BASE || 'http://127.0.0.1:8765/ecosystem/?preview=1';

test.describe('ecosystem D3', () => {
  test('loads without console errors', async ({ page }) => {
    const errors = [];
    page.on('console', (msg) => {
      if (msg.type() !== 'error') return;
      const text = msg.text();
      if (/Failed to load resource.*404/.test(text)) return;
      errors.push(text);
    });
    page.on('pageerror', (err) => errors.push(String(err)));
    await page.goto(`${BASE}&state=overview`, { waitUntil: 'networkidle', timeout: 60000 });
    await page.waitForSelector('body[data-eco-ready="1"]', { timeout: 45000 });
    expect(errors, errors.join('\n')).toEqual([]);
  });

  test('screenshots', async ({ page }) => {
    const shots = [
      { name: 'overview', url: `${BASE}&state=overview` },
      { name: 'actor-selected', url: `${BASE}&state=selected&actor=pe-emprende-up-climatech-rein-hub-peru` },
      { name: 'ego-2hop', url: `${BASE}&state=ego&depth=2&actor=pe-emprende-up-climatech-rein-hub-peru` },
      { name: 'filters', url: `${BASE}&state=filters&country=PE&cats=accelerator,government,funder` },
      { name: 'mobile-selected', url: `${BASE}&state=selected&mobile=1&actor=pe-emprende-up-climatech-rein-hub-peru` },
    ];
    for (const s of shots) {
      await page.goto(s.url, { waitUntil: 'networkidle', timeout: 60000 });
      await page.waitForSelector('body[data-eco-ready="1"]', { timeout: 45000 });
      await page.waitForTimeout(800);
      await page.screenshot({ path: path.join(OUT, `${s.name}.png`), fullPage: true });
    }
  });
});
