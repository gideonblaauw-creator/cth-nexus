#!/usr/bin/env node
/**
 * Render map-wire.html → PNG (3000px) + PDF; map-wire-mobile.html → portrait PNG.
 */
import puppeteer from 'puppeteer';
import { fileURLToPath } from 'url';
import path from 'path';

const dir = path.dirname(fileURLToPath(import.meta.url));
const chrome = process.env.CHROME_PATH || '/usr/local/bin/google-chrome';

async function renderLandscape() {
  const browser = await puppeteer.launch({
    executablePath: chrome,
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox'],
  });
  const page = await browser.newPage();
  const html = path.join(dir, 'map-wire.html');
  await page.goto(`file://${html}`, { waitUntil: 'networkidle0' });
  const el = await page.$('#wire-landscape');
  const box = await el.boundingBox();
  const width = 3000;
  const height = Math.ceil(box.height) + 20;
  await page.setViewport({ width, height, deviceScaleFactor: 1 });
  await page.goto(`file://${html}`, { waitUntil: 'networkidle0' });
  await page.screenshot({
    path: path.join(dir, 'map-wire.png'),
    fullPage: true,
    type: 'png',
  });
  await page.pdf({
    path: path.join(dir, 'map-wire.pdf'),
    width: `${width}px`,
    height: `${height}px`,
    printBackground: true,
    margin: { top: '8mm', bottom: '8mm', left: '8mm', right: '8mm' },
  });
  await browser.close();
  console.log(`Landscape: ${width}x${height}`);
}

async function renderMobile() {
  const browser = await puppeteer.launch({
    executablePath: chrome,
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox'],
  });
  const page = await browser.newPage();
  const html = path.join(dir, 'map-wire-mobile.html');
  await page.setViewport({ width: 1080, height: 1200, deviceScaleFactor: 2 });
  await page.goto(`file://${html}`, { waitUntil: 'networkidle0' });
  await page.screenshot({
    path: path.join(dir, 'map-wire-mobile.png'),
    fullPage: true,
    type: 'png',
  });
  await browser.close();
  console.log('Mobile: map-wire-mobile.png');
}

await renderLandscape();
await renderMobile();
