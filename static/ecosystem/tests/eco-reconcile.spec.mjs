import { test, expect } from '@playwright/test';
import path from 'path';
import { fileURLToPath } from 'url';
import { readFile } from 'fs/promises';
import {
  countCrossCountryPolicyEdges,
  storyContext,
} from '../story.mjs';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const DATA = path.join(__dirname, '..', 'data');
const BASE = process.env.ECO_BASE || 'http://127.0.0.1:8797/ecosystem/';

test('policy bundle has no cross-country issues_policy / addresses_challenge edges', async () => {
  const [actors, policies, policyRels, story] = await Promise.all([
    readFile(path.join(DATA, 'actors.json'), 'utf8').then(JSON.parse),
    readFile(path.join(DATA, 'policies.json'), 'utf8').then(JSON.parse),
    readFile(path.join(DATA, 'policy_relations.json'), 'utf8').then(JSON.parse),
    readFile(path.join(DATA, 'story-chapters.json'), 'utf8').then(JSON.parse),
  ]);
  const byId = new Map(actors.map((a) => [a.id, a]));
  const policiesById = new Map(policies.filter((p) => p.id).map((p) => [p.id, p]));
  const ctx = storyContext({ byId, policiesById, challenges: story.challenges });
  expect(countCrossCountryPolicyEdges(policyRels, ctx)).toBe(0);
});

test.describe('ecosystem public reconcile', () => {
  test('loads signed-out without auth redirect', async ({ page }) => {
    await page.goto(BASE, { waitUntil: 'domcontentloaded', timeout: 60000 });
    await page.waitForSelector('body[data-eco-ready="1"]', { timeout: 45000 });
    expect(page.url()).toMatch(/\/ecosystem\//);
    await expect(page.locator('#stat-actors')).not.toHaveText('—');
    const n = parseInt(await page.locator('#stat-actors').innerText(), 10);
    expect(n).toBeGreaterThan(0);
  });

  test('actor cards tab shows cards', async ({ page }) => {
    await page.goto(`${BASE}?preview=1`, { waitUntil: 'domcontentloaded', timeout: 60000 });
    await page.waitForSelector('body[data-eco-ready="1"]', { timeout: 45000 });
    await expect(page.locator('#stat-actors')).not.toHaveText('—');
    await page.locator('[data-view-tab="cards"]').click();
    await expect(page.locator('#actor-grid .actor-card').first()).toBeVisible({ timeout: 30000 });
    const count = await page.locator('#actor-grid .actor-card').count();
    expect(count).toBeGreaterThan(0);
  });

  test('map canvas renders', async ({ page }) => {
    const errors = [];
    page.on('pageerror', (err) => errors.push(String(err)));
    await page.goto(`${BASE}?preview=1`, { waitUntil: 'domcontentloaded', timeout: 60000 });
    await page.waitForSelector('body[data-eco-ready="1"]', { timeout: 45000 });
    await expect(page.locator('.maplibregl-canvas')).toBeVisible();
    await page.waitForTimeout(2500);
    expect(errors.filter((e) => /circle-radius|zoom/.test(e))).toEqual([]);
  });
});
