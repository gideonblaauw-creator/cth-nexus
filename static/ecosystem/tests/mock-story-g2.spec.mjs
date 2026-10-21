import { test, expect } from '@playwright/test';
import path from 'path';
import { fileURLToPath } from 'url';
import { mkdir } from 'fs/promises';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ARTIFACTS = path.join(__dirname, '..', 'mock', 'story-directions', 'screenshots');
const BASE = (process.env.MOCK_BASE_URL || 'http://127.0.0.1:8765').replace(/\/?$/, '');
const G2 = `${BASE}/ecosystem/mock/story-directions/g2/index.html`;

test.describe('mock story direction G2', () => {
  test('layout, challenge deep link, step interaction', async ({ page }) => {
    const errors = [];
    page.on('pageerror', (err) => errors.push(String(err)));

    await page.goto(`${G2}?challenge=PE-2-agua`, { waitUntil: 'domcontentloaded', timeout: 60000 });
    await page.waitForSelector('.g2-step', { timeout: 45000 });
    expect(page.url()).toContain('challenge=PE-2-agua');

    await expect(page.locator('.g2-triptych')).toBeVisible();
    await expect(page.locator('[data-g2-map]')).toBeVisible();
    await expect(page.locator('[data-g2-graph]')).toBeVisible();
    await expect(page.locator('[data-g2-inspector]')).toBeVisible();

    const stat = page.locator('[data-g2-stat]');
    await expect(stat).toContainText('12.000 m³');
    await expect(stat.locator('a[href*="gob.pe/institucion/produce"]')).toBeVisible();

    const steps = page.locator('.g2-step');
    await expect(steps).toHaveCount(6);
    await steps.nth(2).click();
    await expect(steps.nth(2)).toHaveClass(/on/);
    await expect(page.locator('[data-g2-inspector] a[href^="http"]')).toBeVisible();

    await page.selectOption('#startup-select', 'pe-uqhu');
    await page.waitForSelector('.g2-step.on');
    await expect(page.locator('[data-g2-stat]')).toHaveClass(/hidden/);

    await page.selectOption('#mock-challenge-select', { index: 1 });
    await page.waitForTimeout(300);

    expect(errors.filter((e) => !/Sigma/.test(e))).toEqual([]);
  });

  test('screenshots desktop and mobile', async ({ page }) => {
    await mkdir(ARTIFACTS, { recursive: true });
    await page.goto(G2, { waitUntil: 'domcontentloaded', timeout: 60000 });
    await page.waitForSelector('.g2-step', { timeout: 45000 });
    await page.waitForTimeout(3500);

    await page.setViewportSize({ width: 1440, height: 900 });
    await page.screenshot({
      path: path.join(ARTIFACTS, 'direction-g2-desktop.png'),
      fullPage: false,
    });

    await page.setViewportSize({ width: 390, height: 844 });
    await page.waitForTimeout(500);
    await page.screenshot({
      path: path.join(ARTIFACTS, 'direction-g2-mobile.png'),
      fullPage: true,
    });
  });
});
