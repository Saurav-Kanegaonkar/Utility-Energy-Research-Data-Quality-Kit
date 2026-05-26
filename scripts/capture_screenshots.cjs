const fs = require("fs");
const os = require("os");
const path = require("path");
const { createRequire } = require("module");

function loadPlaywright() {
  const bundledModules = path.join(
    os.homedir(),
    ".cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules"
  );
  try {
    return require("playwright");
  } catch (error) {
    return createRequire(path.join(bundledModules, "noop.js"))("playwright");
  }
}

async function run() {
  const { chromium } = loadPlaywright();
  const root = path.resolve(__dirname, "..");
  const imageDir = path.join(root, "docs", "images");
  fs.mkdirSync(imageDir, { recursive: true });

  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({
    viewport: { width: 1440, height: 1050 },
    deviceScaleFactor: 1,
  });

  await page.goto("http://127.0.0.1:4873", { waitUntil: "networkidle" });
  await page.screenshot({ path: path.join(imageDir, "quality-queue.png"), fullPage: true });

  await page.click('[data-view="updates"]');
  await page.waitForTimeout(350);
  await page.screenshot({ path: path.join(imageDir, "tool-updates.png"), fullPage: true });

  await page.click('[data-view="requests"]');
  await page.waitForTimeout(350);
  await page.screenshot({ path: path.join(imageDir, "research-triage.png"), fullPage: true });

  await page.setViewportSize({ width: 390, height: 900 });
  await page.click('[data-view="quality"]');
  await page.waitForTimeout(350);
  await page.screenshot({ path: path.join(imageDir, "mobile-check.png"), fullPage: true });

  await browser.close();
  console.log("Captured README screenshots.");
}

run().catch((error) => {
  console.error(error);
  process.exit(1);
});
