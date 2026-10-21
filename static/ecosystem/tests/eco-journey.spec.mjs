import { test, expect } from '@playwright/test';
import path from 'path';
import { fileURLToPath } from 'url';
import { readFile } from 'fs/promises';
import { mkdir } from 'fs/promises';
import {
  boxesOverlap,
  buildJourneyModel,
  fittedLabelBoxes,
  isJourneyEdge,
  streetPinFor,
} from '../journey.mjs';
import { isPublicGraphRelation } from '../story.mjs';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const DATA = path.join(__dirname, '..', 'data');
const SHOTS = path.join(__dirname, '..', 'screenshots-journey');
const BASE = (process.env.ECO_BASE || 'http://127.0.0.1:8797/ecosystem/').replace(/\/?$/, '/');

function eco(qs) {
  return `${BASE}?${qs}`;
}

async function loadBundle() {
  const [actors, relations, story, dataRels] = await Promise.all([
    readFile(path.join(DATA, 'actors.json'), 'utf8').then(JSON.parse),
    readFile(path.join(DATA, 'relations.json'), 'utf8').then(JSON.parse),
    readFile(path.join(DATA, 'story-chapters.json'), 'utf8').then(JSON.parse),
    readFile(path.join(DATA, 'data_relations.json'), 'utf8').then(JSON.parse),
  ]);
  return { actors, relations, story, dataRels };
}

test('street pins require address precision and a street string', async () => {
  const { actors } = await loadBundle();
  const byId = new Map(actors.map((a) => [a.id, a]));
  expect(streetPinFor(byId.get('pe-yakufil'))).toBeNull();
  expect(streetPinFor(byId.get('pe-uqhu'))).toBeNull();
  expect(streetPinFor(byId.get('pe-yakusmart'))).toBeNull();
  expect(streetPinFor(byId.get('pe-cleantechhub'))).toBeNull();
  const produce = streetPinFor(byId.get('pe-produce-ministerio-de-la-produccion'));
  expect(produce?.precision).toBe('address');
  expect(produce.lat).toBeCloseTo(-12.098, 2);

  expect(streetPinFor({
    country: 'Peru',
    name: 'City',
    geo: { precision: 'city', lat: -12.04, lng: -77.04, address: 'Lima' },
  })).toBeNull();
  expect(streetPinFor({
    country: 'Peru',
    name: 'Country',
    geo: { precision: 'country', lat: -9.19, lng: -75.01, address: 'Peru' },
  })).toBeNull();
  expect(streetPinFor({
    country: 'Peru',
    name: 'No street',
    geo: { precision: 'address', lat: -12.07, lng: -77.08 },
  })).toBeNull();
});

test('journey graph uses only public verbatim relations', async () => {
  const { actors, relations, story, dataRels } = await loadBundle();
  const hidden = relations.filter((r) => !isPublicGraphRelation(r));
  expect(hidden.length).toBeGreaterThan(0);
  hidden.forEach((r) => expect(isJourneyEdge(r)).toBe(false));

  const yakufil = buildJourneyModel({
    actors,
    relations,
    dataRelations: dataRels,
    storyConfig: story,
    challengeId: 'challenge:PE-2-agua',
    startupId: 'pe-yakufil',
    lang: 'ES',
  });
  expect(yakufil.edges.length).toBeGreaterThan(0);
  expect(yakufil.edges.every((e) => isPublicGraphRelation(e) && e.evidence && e.source_url)).toBe(true);
  expect(yakufil.edges.map((e) => e.source_url).join(' ')).toContain('unsa.edu.pe');
  expect(yakufil.pins.map((p) => p.id)).not.toContain('pe-yakufil');
  expect(yakufil.unknown.map((u) => u.id)).toContain('pe-yakufil');
  expect(yakufil.dataRows.every((r) => r.plottable === false)).toBe(true);

  const yakusmart = buildJourneyModel({
    actors,
    relations,
    dataRelations: dataRels,
    storyConfig: story,
    challengeId: 'challenge:PE-2-agua',
    startupId: 'pe-yakusmart',
    lang: 'ES',
  });
  expect(yakusmart.edges).toEqual([]);
  expect(yakusmart.stat?.stat).toBe('12.000 m³');
  expect(yakusmart.nodes).not.toContain('pe-emprende-up-climatech-rein-hub-peru');
});

test('alternating labels do not overlap on desktop or mobile widths', () => {
  const labels = ['YakuSmart', 'ProInnóvate', 'Agua & cuencas', 'Emprende UP', 'Produce', 'ANA'];
  for (const width of [360, 700, 900]) {
    const { overlap } = fittedLabelBoxes(labels, width, 320);
    expect(overlap, `overlap at ${width}px`).toBe(false);
  }
  const stacked = [
    { x: 10, y: 10, w: 40, h: 14 },
    { x: 20, y: 12, w: 40, h: 14 },
  ];
  expect(boxesOverlap(stacked)).toBe(true);
});

async function waitJourney(page) {
  await page.waitForSelector('body[data-journey-ready="1"]', { timeout: 45000 });
  await page.waitForFunction(() => {
    const el = document.querySelector('#journey-graph');
    return Number(el?.dataset.journeyGraphNodes || 0) > 0
      && el?.dataset.journeyLabelOverlap === '0';
  }, { timeout: 20000 });
}

async function expectDataMapFills(page) {
  await page.waitForFunction(() => {
    const el = document.querySelector('#journey-data-map');
    const canvas = el?.querySelector('canvas.maplibregl-canvas');
    if (!el || !canvas) return false;
    const box = el.getBoundingClientRect().width;
    const canvasBox = canvas.getBoundingClientRect().width;
    const dpr = window.devicePixelRatio || 1;
    return box > 80
      && canvasBox >= box * 0.9
      && canvas.width >= Math.floor(box * dpr * 0.9);
  }, undefined, { timeout: 15000 });
  const measured = await page.locator('#journey-data-map').evaluate((el) => {
    const canvas = el.querySelector('canvas.maplibregl-canvas');
    const box = el.getBoundingClientRect().width;
    const canvasBox = canvas?.getBoundingClientRect().width || 0;
    const dpr = window.devicePixelRatio || 1;
    return { box, canvasBox, attr: canvas?.width || 0, dpr };
  });
  expect(measured.canvasBox / measured.box, JSON.stringify(measured)).toBeGreaterThanOrEqual(0.9);
  expect(measured.attr / (measured.box * measured.dpr), JSON.stringify(measured)).toBeGreaterThanOrEqual(0.9);
}

test('live journey view desktop and mobile', async ({ page }) => {
  const errors = [];
  page.on('pageerror', (err) => errors.push(String(err)));

  await page.setViewportSize({ width: 1440, height: 1000 });
  await page.goto(eco('view=journey&challenge=PE-2-agua'), { waitUntil: 'domcontentloaded', timeout: 60000 });
  await waitJourney(page);

  expect(page.url()).toContain('challenge=PE-2-agua');
  await expect(page.locator('.ph-title')).toHaveText('Camino de la startup');
  await expect(page.locator('[data-view-tab="journey"]')).toHaveClass(/active/);
  await expect(page.locator('.journey-triptych')).toBeVisible();
  await expect(page.locator('#journey-map .maplibregl-canvas')).toBeVisible();
  await expect(page.locator('#journey-graph canvas').first()).toBeVisible();
  await expect(page.locator('.journey-step')).toHaveCount(6);

  const pins = await page.evaluate(() => window.__journey.listMapPins());
  expect(pins).toEqual([]);
  const unknown = await page.evaluate(() => window.__journey.listUnknown().map((u) => u.label).join(' '));
  expect(unknown).toMatch(/Yakufil/);
  await expect(page.locator('#journey-unknown')).toContainText('Ubicación desconocida');

  const edges = await page.evaluate(() => window.__journey.listEdges());
  expect(edges.length).toBeGreaterThan(0);
  expect(edges.every((e) => e.evidence && /^https?:\/\//.test(e.source_url))).toBe(true);
  await expect(page.locator('#journey-inspector a[href*="unsa.edu.pe"]')).toBeVisible();

  const dataBox = await page.locator('#journey-data').boundingBox();
  const triptych = await page.locator('.journey-triptych').boundingBox();
  expect(dataBox.width).toBeGreaterThan(triptych.width * 0.9);
  await expect(page.locator('#journey-data-map')).toBeVisible();
  await expectDataMapFills(page);
  await expect(page.locator('#journey-data')).toContainText('Ubicación desconocida');
  const dataPins = await page.evaluate(() => window.__journey.dataPinCount());
  expect(dataPins).toBe(0);

  const leaked = await page.locator('#panel-journey').innerHTML();
  expect(leaked).not.toMatch(/drive\.google|canva\.com|mailto:|tel:/i);
  expect(leaked).not.toMatch(/[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}/);
  expect(leaked).not.toContain('Calle Uno Oeste');
  expect(leaked).not.toContain('Bogotá');

  await page.locator('.journey-step').nth(1).click();
  await expect(page.locator('.journey-step').nth(1)).toHaveClass(/on/);
  await expect(page.locator('#journey-inspector')).toContainText(/Sin relación pública de política/);

  await page.selectOption('#journey-startup', 'pe-yakusmart');
  await page.waitForFunction(() => window.__journey.startupId() === 'pe-yakusmart');
  await expect(page.locator('#journey-stat')).toContainText('12.000 m³');
  await expect(page.locator('#journey-stat a[href*="gob.pe"]')).toBeVisible();
  const smartEdges = await page.evaluate(() => window.__journey.listEdges());
  expect(smartEdges).toEqual([]);

  await page.selectOption('#journey-challenge', 'challenge:PE-1-bosques');
  await page.waitForFunction(() => window.__journey.challengeId() === 'challenge:PE-1-bosques');
  expect(page.url()).toContain('challenge=PE-1-bosques');

  await page.locator('[data-lang-btn="EN"]').click();
  await expect(page.locator('.ph-title')).toHaveText('Startup journey');
  await expect(page.locator('[data-view-tab="journey"]')).toHaveText('Startup journey');
  await expect(page.locator('#journey-unknown')).toContainText('Location unknown');
  await expect(page.locator('#journey-data .journey-kicker')).toHaveText('Data map');

  await page.locator('[data-view-tab="cards"]').click();
  await expect(page.locator('#actor-grid .actor-card').first()).toBeVisible();

  await page.locator('[data-view-tab="journey"]').click();
  await page.locator('[data-lang-btn="ES"]').click();
  await page.selectOption('#journey-challenge', 'challenge:PE-2-agua');
  await page.selectOption('#journey-startup', 'pe-yakufil');
  await waitJourney(page);
  await expect(page.locator('#journey-inspector a[href*="unsa.edu.pe"]')).toBeVisible();

  await mkdir(SHOTS, { recursive: true });
  await page.setViewportSize({ width: 1440, height: 1000 });
  await expectDataMapFills(page);
  await page.waitForTimeout(700);
  await page.screenshot({ path: path.join(SHOTS, 'journey-desktop.png'), fullPage: true });

  await page.setViewportSize({ width: 390, height: 844 });
  await waitJourney(page);
  await expectDataMapFills(page);
  await page.waitForTimeout(500);
  const columns = await page.locator('.journey-triptych').evaluate((el) => getComputedStyle(el).gridTemplateColumns.split(' ').filter(Boolean));
  expect(columns.length).toBe(1);
  const overlap = await page.evaluate(() => document.querySelector('#journey-graph')?.dataset.journeyLabelOverlap);
  expect(overlap).toBe('0');
  await page.screenshot({ path: path.join(SHOTS, 'journey-mobile.png'), fullPage: true });

  expect(errors.filter((e) => !/Sigma/.test(e))).toEqual([]);
});
