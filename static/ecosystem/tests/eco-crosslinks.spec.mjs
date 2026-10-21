import { test, expect } from '@playwright/test';
import { readFileSync, existsSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const __dir = dirname(fileURLToPath(import.meta.url));
const REPO = join(__dir, '../../..');
const DATA = join(REPO, 'static/ecosystem/data/nexus-crosslinks.json');

function loadCrosslinks() {
  return JSON.parse(readFileSync(DATA, 'utf8'));
}

function resolveOnDisk(href) {
  if (href.startsWith('/s/')) {
    const slug = href.replace(/^\/s\//, '').replace(/\/$/, '');
    return join(REPO, 'onepagers/sites', slug, 'index.html');
  }
  if (href.startsWith('/hubs/')) {
    const slug = href.replace(/^\/hubs\//, '').replace(/\/$/, '');
    return join(REPO, 'site/cth-static/hubs', slug, 'index.html');
  }
  if (href.startsWith('/ideas/')) {
    return null;
  }
  return null;
}

function sampleLinks(cross) {
  const out = [];
  const push = (row) => {
    if (row?.href) out.push(row);
  };
  for (const panel of Object.values(cross.byChallenge || {})) {
    for (const key of ['ideas', 'solutions', 'startups']) {
      (panel[key] || []).forEach(push);
    }
  }
  for (const rows of Object.values(cross.byPolicy || {})) {
    rows.forEach(push);
  }
  const actors = JSON.parse(readFileSync(join(REPO, 'static/ecosystem/data/actors.json'), 'utf8'));
  for (const a of actors) {
    const slug = a.nexus?.card_slug;
    if (slug) push({ href: `/s/${slug}/`, label: a.name });
    const hub = a.nexus?.hub_slug;
    if (hub) push({ href: `/hubs/${hub}/`, label: a.name });
  }
  const seen = new Set();
  const uniq = [];
  for (const row of out) {
    if (seen.has(row.href)) continue;
    seen.add(row.href);
    uniq.push(row);
  }
  const step = Math.max(1, Math.floor(uniq.length / 12));
  return uniq.filter((_, i) => i % step === 0).slice(0, 24);
}

test('nexus-crosslinks bundle exists with counts', async () => {
  const cross = loadCrosslinks();
  expect(cross.version).toBe(1);
  expect(cross.valid.s.length).toBeGreaterThan(0);
  expect(cross.counts.s_pages).toBe(cross.valid.s.length);
});

test('sampled crosslinks resolve on disk or ideas manifest', async () => {
  const cross = loadCrosslinks();
  const ideasOk = new Set(cross.valid.ideas || []);
  const samples = sampleLinks(cross);
  expect(samples.length).toBeGreaterThan(0);
  for (const row of samples) {
    const path = resolveOnDisk(row.href);
    if (path) {
      expect(existsSync(path), `missing file for ${row.href}`).toBeTruthy();
    } else if (row.href.startsWith('/ideas/')) {
      expect(ideasOk.has(row.href), `ideas href not in manifest: ${row.href}`).toBeTruthy();
    } else {
      throw new Error(`unknown href type: ${row.href}`);
    }
  }
});
