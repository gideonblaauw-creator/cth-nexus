import { test, expect } from '@playwright/test';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const OUT = path.join(__dirname, '..', 'screenshots-d5');
const BASE = (process.env.ECO_BASE || 'http://127.0.0.1:8797/ecosystem/').replace(/\/?$/, '/');
function ecoQuery(qs) {
  return BASE.includes('?') ? `${BASE}&${qs}` : `${BASE}?${qs}`;
}

const chapters = [
  { name: 'ch1-challenges', chapter: 0 },
  { name: 'ch2-policy', chapter: 1 },
  { name: 'ch3-capital', chapter: 2 },
  { name: 'ch4-hubs', chapter: 3 },
  { name: 'ch5-partnerships', chapter: 4 },
  { name: 'ch5-constellation-agua-uqhu', chapter: 4, constellation: 'agua-uqhu', closeup: 1 },
];

test('guided story chapters', async ({ page }) => {
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

  await mkdir(OUT);
  for (const ch of chapters) {
    let url = ecoQuery(`preview=1&v=d5&view=story&state=story&chapter=${ch.chapter}`);
    if (ch.constellation) url += `&constellation=${ch.constellation}&closeup=${ch.closeup || 0}`;
    await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 });
    await expect(page.locator('#stat-actors')).not.toHaveText('—', { timeout: 60000 });
    await page.waitForTimeout(1200);
    await page.screenshot({ path: path.join(OUT, `${ch.name}.png`), fullPage: true });
  }

  const counts = await page.evaluate(() => window.__storyEdgeCounts || []);
  console.log('STORY_EDGE_COUNTS', JSON.stringify(counts, null, 2));
  expect(errors, errors.join('\n')).toEqual([]);
  expect(counts.length).toBe(5);
});

async function mkdir(p) {
  const { mkdir: mk } = await import('fs/promises');
  await mk(p, { recursive: true });
}
