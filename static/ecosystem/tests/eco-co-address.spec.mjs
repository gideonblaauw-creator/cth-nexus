import { test, expect } from '@playwright/test';
import path from 'path';
import { fileURLToPath } from 'url';
import { readFile, mkdir } from 'fs/promises';
import { actorCountryCode, redactPublicStreetText, visibleStreetAddress } from '../geo-utils.mjs';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const DATA = path.join(__dirname, '..', 'data');
const SHOTS = path.join(__dirname, '..', 'screenshots-co');
const BASE = (process.env.ECO_BASE || 'http://127.0.0.1:8797/ecosystem/').replace(/\/?$/, '/');

function eco(qs) {
  return `${BASE}?${qs}`;
}

function streetFragments(actor) {
  const bits = [];
  const street = String(actor?.geo?.address || '').trim();
  if (street) bits.push(street);
  const desc = String(actor?.card?.description || '');
  const row = desc.match(/direcci[oó]n\s*\|\s*([^|\n]+)/i);
  if (row) {
    const value = row[1].trim();
    if (value && !/^pendiente/i.test(value)) bits.push(value);
  }
  return [...new Set(bits)];
}

test('Colombia actor popup shows no street address', async ({ page }) => {
  const actors = JSON.parse(await readFile(path.join(DATA, 'actors.json'), 'utf8'));
  const colombia = actors.filter((a) => actorCountryCode(a) === 'CO');
  expect(colombia.length).toBeGreaterThan(0);
  const bancoldex = actors.find((a) => a.id === 'co-bancoldex');
  expect(bancoldex?.geo?.address).toBeTruthy();
  expect(visibleStreetAddress(bancoldex)).toBe('');
  expect(bancoldex.geo.lat).toBeCloseTo(4.615712, 4);
  expect(bancoldex.geo.lng).toBeCloseTo(-74.071314, 4);

  const peru = actors.find((a) => a.id === 'pe-profonanpe');
  expect(visibleStreetAddress(peru)).toBe(peru.geo.address);
  expect(redactPublicStreetText(peru, peru.card.description)).toContain('Dirección');

  const hiddenBits = colombia.flatMap(streetFragments);
  expect(hiddenBits).toContain(bancoldex.geo.address);
  colombia.forEach((actor) => {
    expect(visibleStreetAddress(actor), actor.id).toBe('');
    const rendered = redactPublicStreetText(actor, actor.card?.description || '');
    hiddenBits.forEach((bit) => {
      if (streetFragments(actor).includes(bit) || String(actor.geo?.address || '') === bit) {
        expect(rendered, actor.id).not.toContain(bit);
      }
    });
  });

  await page.goto(eco('preview=1&state=selected&actor=co-bancoldex'), {
    waitUntil: 'domcontentloaded',
    timeout: 60000,
  });
  await expect(page.locator('#inspector h2')).toContainText('Bancóldex', { timeout: 30000 });
  const popup = page.locator('.eco-pin-popup');
  await expect(popup).toBeVisible({ timeout: 20000 });
  await expect(popup).toContainText('Bancóldex');
  await expect(popup).toContainText('Bogotá');
  await expect(popup.locator('.eco-pin-address')).toHaveCount(0);
  for (const bit of hiddenBits) {
    await expect(popup).not.toContainText(bit);
    await expect(page.locator('#inspector')).not.toContainText(bit);
  }

  await page.waitForFunction(() => window.__ecoMap && !window.__ecoMap.isMoving());
  const coords = await page.evaluate((id) => {
    const src = window.__ecoMap?.getSource('actors');
    const data = src?._data || src?.serialize?.().data;
    const feat = data?.features?.find((f) => f.properties?.id === id);
    return feat ? feat.geometry.coordinates : null;
  }, 'co-bancoldex');
  expect(coords?.[0]).toBeCloseTo(bancoldex.geo.lng, 4);
  expect(coords?.[1]).toBeCloseTo(bancoldex.geo.lat, 4);

  const tip = await page.evaluate((id) => {
    const map = window.__ecoMap;
    const canvas = map.getCanvas();
    const src = map.getSource('actors');
    const data = src._data || src.serialize().data;
    const feat = data.features.find((f) => f.properties?.id === id);
    const point = map.project(feat.geometry.coordinates);
    return {
      x: point.x,
      y: point.y,
      w: canvas.clientWidth,
      h: canvas.clientHeight,
    };
  }, 'co-bancoldex');
  if (tip.x >= 8 && tip.y >= 8 && tip.x < tip.w - 8 && tip.y < tip.h - 8) {
    await page.locator('.eco-pin-popup').evaluate((el) => { el.style.pointerEvents = 'none'; });
    await page.locator('#eco-map canvas').hover({ position: { x: Math.round(tip.x), y: Math.round(tip.y) } });
    const tooltip = page.locator('.eco-pin-tooltip');
    await expect(tooltip).toBeVisible({ timeout: 5000 });
    for (const bit of hiddenBits) {
      await expect(tooltip).not.toContainText(bit);
    }
    await expect(tooltip.locator('.eco-pin-address')).toHaveCount(0);
  }

  await mkdir(SHOTS, { recursive: true });
  await page.screenshot({
    path: path.join(SHOTS, 'colombia-actor-popup.png'),
    fullPage: false,
  });

  await page.locator('[data-view-tab="cards"]').click();
  await expect(page.locator('#actor-grid .actor-card').first()).toBeVisible();
  for (const actor of colombia) {
    const card = page.locator(`.actor-card[data-id="${actor.id}"]`);
    await expect(card).toHaveCount(1);
    const text = await card.innerText();
    for (const bit of streetFragments(actor)) {
      expect(text, actor.id).not.toContain(bit);
    }
  }

  const peruCard = page.locator('.actor-card[data-id="pe-profonanpe"]');
  await expect(peruCard).toContainText('Av. Parque Gonzales Prada');

  await page.goto(eco('preview=1&state=selected&actor=pe-profonanpe'), {
    waitUntil: 'domcontentloaded',
    timeout: 60000,
  });
  const peruPopup = page.locator('.eco-pin-popup');
  await expect(peruPopup).toBeVisible({ timeout: 20000 });
  await expect(peruPopup.locator('.eco-pin-address')).toHaveText(peru.geo.address);
});
