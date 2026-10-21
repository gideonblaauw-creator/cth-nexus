import { test, expect } from '@playwright/test';
import path from 'path';
import { fileURLToPath } from 'url';
import { readFile } from 'fs/promises';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const DATA = path.join(__dirname, '..', 'data');
const BASE = (process.env.ECO_BASE || 'http://127.0.0.1:8797/ecosystem/').replace(/\/?$/, '/');

test.describe('ecosystem actor cards', () => {
  test('cards show description expand and vetted relations', async ({ page }) => {
    const relBundle = JSON.parse(await readFile(path.join(DATA, 'actor_relations.json'), 'utf8'));
    const sample = relBundle.relations.find((r) => r.from_id === 'pe-produce-ministerio-de-la-produccion');
    expect(sample?.source_url).toBeTruthy();

    await page.goto(`${BASE}?preview=1`, { waitUntil: 'domcontentloaded', timeout: 60000 });
    await expect(page.locator('#stat-actors')).not.toHaveText('—', { timeout: 60000 });
    await page.locator('[data-view-tab="cards"]').click();
    await page.waitForSelector('.actor-card', { timeout: 30000 });

    const bancoldex = page.locator('.actor-card').filter({ hasText: 'Bancóldex' }).first();
    await expect(bancoldex.locator('.ac-desc, .ac-desc-block')).toBeVisible();

    const produceCard = page.locator('.actor-card').filter({ hasText: 'PRODUCE' }).first();
    await expect(produceCard.locator('.ac-relations')).toBeVisible();
    await expect(produceCard.locator('.ac-rel-src')).toHaveCount(1, { timeout: 5000 });
    await expect(produceCard.locator('a.ac-rel-name')).toContainText(/ProInnóvate/i);
  });
});
