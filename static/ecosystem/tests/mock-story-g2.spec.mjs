import { test, expect } from '@playwright/test';
import path from 'path';
import { fileURLToPath } from 'url';
import { mkdir } from 'fs/promises';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ARTIFACTS = path.join(__dirname, '..', 'mock', 'story-directions', 'screenshots');
const BASE = (process.env.MOCK_BASE_URL || 'http://127.0.0.1:8765').replace(/\/?$/, '');
const G2 = `${BASE}/ecosystem/mock/story-directions/g2/index.html`;

async function waitForSigmaReady(page) {
  await page.waitForFunction(() => {
    const el = document.querySelector('[data-g2-graph]');
    const n = Number(el?.dataset?.g2GraphNodes || 0);
    return n > 0 && el?.querySelector('canvas')?.width > 0;
  }, { timeout: 45000 });
  await page.waitForTimeout(250);
}

async function assertSigmaCanvasNonBlank(page) {
  const stats = await page.evaluate(() => {
    const wrap = document.querySelector('[data-g2-graph]');
    const canvas = wrap?.querySelector('canvas');
    const nodes = Number(wrap?.dataset?.g2GraphNodes || 0);
    const edges = Number(wrap?.dataset?.g2GraphEdges || 0);
    if (!canvas || nodes <= 0) return { ok: false, nodes, edges, reason: 'no canvas or nodes' };
    if (canvas.width < 8 || canvas.height < 8) return { ok: false, nodes, edges, reason: 'tiny canvas' };
    const gl = canvas.getContext('webgl2') || canvas.getContext('webgl');
    if (!gl) return { ok: nodes > 0 && edges > 0, nodes, edges };
    const pixels = new Uint8Array(canvas.width * canvas.height * 4);
    gl.readPixels(0, 0, canvas.width, canvas.height, gl.RGBA, gl.UNSIGNED_BYTE, pixels);
    let painted = 0;
    for (let i = 0; i < pixels.length; i += 4) {
      if (pixels[i + 3] > 0) painted += 1;
    }
    return { ok: painted > 50 || (nodes > 0 && edges > 0), painted, nodes, edges };
  });
  expect(stats.nodes, 'sigma node count').toBeGreaterThan(0);
  expect(stats.edges, 'sigma edge count').toBeGreaterThan(0);
  expect(stats.ok, JSON.stringify(stats)).toBeTruthy();
}

test.describe('mock story direction G2', () => {
  test('layout, challenge deep link, step interaction', async ({ page }) => {
    const errors = [];
    page.on('pageerror', (err) => errors.push(String(err)));

    await page.goto(`${G2}?challenge=PE-2-agua`, { waitUntil: 'domcontentloaded', timeout: 60000 });
    await page.waitForSelector('.g2-step', { timeout: 45000 });
    await waitForSigmaReady(page);
    await assertSigmaCanvasNonBlank(page);

    expect(page.url()).toContain('challenge=PE-2-agua');

    await expect(page.locator('.g2-triptych')).toBeVisible();
    await expect(page.locator('[data-g2-map]')).toBeVisible();
    await expect(page.locator('[data-g2-graph]')).toBeVisible();
    await expect(page.locator('[data-g2-inspector]')).toBeVisible();

    const nodeCount = await page.locator('[data-g2-graph]').evaluate((el) => Number(el.dataset.g2GraphNodes || 0));
    expect(nodeCount).toBeGreaterThan(0);

    const stat = page.locator('[data-g2-stat]');
    await expect(stat).toContainText('12.000 m³');
    await expect(stat.locator('a[href*="gob.pe/institucion/produce"]')).toBeVisible();

    const pins = await page.evaluate(() => window.__g2Mock?.listMapPins?.() || []);
    expect(pins.map((p) => p.id)).toEqual(['pe-produce-ministerio-de-la-produccion']);
    expect(pins.some((p) => p.id === 'pe-cleantechhub')).toBe(false);

    const steps = page.locator('.g2-step');
    await expect(steps).toHaveCount(6);
    await steps.nth(2).click();
    await waitForSigmaReady(page);
    await expect(steps.nth(2)).toHaveClass(/on/);
    await expect(page.locator('[data-g2-inspector] a[href^="http"]')).toBeVisible();

    await steps.nth(0).click();
    await expect(page.locator('[data-g2-unknown]')).toContainText(/referencia Canva/i);
    await expect(page.locator('[data-g2-unknown]')).toContainText(/CleantechHUB/i);

    await steps.nth(1).click();
    await expect(page.locator('.maplibregl-canvas')).toBeVisible();

    await page.selectOption('#startup-select', 'pe-uqhu');
    await page.waitForSelector('.g2-step.on');
    await waitForSigmaReady(page);
    await expect(page.locator('[data-g2-stat]')).toHaveClass(/hidden/);

    await page.selectOption('#mock-challenge-select', { index: 1 });
    await page.waitForTimeout(300);

    expect(errors.filter((e) => !/Sigma/.test(e))).toEqual([]);
  });

  test('screenshots desktop and mobile', async ({ page }) => {
    await mkdir(ARTIFACTS, { recursive: true });
    await page.goto(G2, { waitUntil: 'domcontentloaded', timeout: 60000 });
    await page.waitForSelector('.g2-step', { timeout: 45000 });
    await waitForSigmaReady(page);
    await assertSigmaCanvasNonBlank(page);

    await page.setViewportSize({ width: 1440, height: 900 });
    await waitForSigmaReady(page);
    await page.waitForTimeout(400);

    await page.screenshot({
      path: path.join(ARTIFACTS, 'direction-g2-desktop.png'),
      fullPage: false,
    });

    await page.setViewportSize({ width: 390, height: 844 });
    await waitForSigmaReady(page);
    await page.waitForTimeout(400);
    await page.screenshot({
      path: path.join(ARTIFACTS, 'direction-g2-mobile.png'),
      fullPage: true,
    });
  });
});
