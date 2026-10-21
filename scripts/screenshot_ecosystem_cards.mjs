#!/usr/bin/env node
/**
 * Capture Ecosystem card grid screenshots (CO, PE, SV) after actors.json loads.
 * Usage: node scripts/screenshot_ecosystem_cards.mjs [baseUrl] [outDir]
 */
import { chromium } from "@playwright/test";
import { mkdir } from "node:fs/promises";
import path from "node:path";

const baseUrl = process.argv[2] || "http://127.0.0.1:8765";
const outDir =
  process.argv[3] || "/opt/cursor/artifacts/screenshots/ecosystem-cards";

const countries = [
  { code: "CO", file: "ecosystem-cards-colombia.png" },
  { code: "PE", file: "ecosystem-cards-peru.png" },
  { code: "SV", file: "ecosystem-cards-el-salvador.png" },
];

await mkdir(outDir, { recursive: true });

const browser = await chromium.launch();
const context = await browser.newContext({
  viewport: { width: 1400, height: 900 },
  deviceScaleFactor: 1,
});

for (const { code, file } of countries) {
  const page = await context.newPage();
  const url = `${baseUrl}/ecosystem/?view=cards&country=${code}`;
  await page.goto(url, { waitUntil: "networkidle", timeout: 120_000 });
  await page.waitForSelector("#actor-grid .actor-card", { timeout: 120_000 });
  await page.waitForTimeout(500);
  const cards = await page.locator("#actor-grid .actor-card").count();
  console.log(`${code}: ${cards} cards visible`);
  await page.screenshot({
    path: path.join(outDir, file),
    fullPage: false,
  });
  await page.close();
}

await browser.close();
console.log(`Saved screenshots to ${outDir}`);
