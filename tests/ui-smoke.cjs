const fs = require("fs");
const path = require("path");
const { chromium } = require("C:/Users/魏旭浩/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/.pnpm/playwright@1.61.1/node_modules/playwright");

const edgePath = "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe";
const outputDir = process.argv[2] || path.join(process.cwd(), ".playwright-mcp", "ui-smoke");
const url = process.argv[3] || "http://127.0.0.1:8080/";

const viewports = [
  { name: "desktop", width: 1440, height: 1000 },
  { name: "mobile", width: 390, height: 844 },
  { name: "mobile-small", width: 360, height: 800 },
];

async function inspectViewport(browser, viewport) {
  const context = await browser.newContext({
    viewport: { width: viewport.width, height: viewport.height },
    deviceScaleFactor: 1,
    isMobile: viewport.width < 600,
    hasTouch: viewport.width < 600,
  });
  const page = await context.newPage();
  await page.goto(url, { waitUntil: "networkidle" });
  await page.waitForSelector("#replyPanel:not([hidden])");

  const metrics = await page.evaluate(() => {
    const selectorMetrics = {};
    for (const selector of ["#memoryButton", "#sendButton", "#optionA", "#optionB", "#messageInput"]) {
      const element = document.querySelector(selector);
      const rect = element.getBoundingClientRect();
      selectorMetrics[selector] = {
        left: Math.round(rect.left),
        right: Math.round(rect.right),
        top: Math.round(rect.top),
        bottom: Math.round(rect.bottom),
      };
    }
    return {
      viewportWidth: window.innerWidth,
      viewportHeight: window.innerHeight,
      documentWidth: document.documentElement.scrollWidth,
      bodyWidth: document.body.scrollWidth,
      selectorMetrics,
    };
  });

  if (metrics.documentWidth > metrics.viewportWidth || metrics.bodyWidth > metrics.viewportWidth) {
    throw new Error(`${viewport.name}: horizontal overflow ${JSON.stringify(metrics)}`);
  }
  for (const [selector, rect] of Object.entries(metrics.selectorMetrics)) {
    if (rect.left < 0 || rect.right > metrics.viewportWidth || rect.top < 0 || rect.bottom > metrics.viewportHeight) {
      throw new Error(`${viewport.name}: ${selector} is outside viewport ${JSON.stringify(rect)}`);
    }
  }

  fs.mkdirSync(outputDir, { recursive: true });
  await page.screenshot({ path: path.join(outputDir, `ui-${viewport.name}.png`) });

  await page.click("#memoryButton");
  await page.waitForSelector("#memoryDrawer.open");
  await page.waitForTimeout(350);
  const drawerVisible = await page.locator("#memoryDrawer").isVisible();
  if (!drawerVisible) throw new Error(`${viewport.name}: memory drawer did not open`);
  const drawerRect = await page.locator("#memoryDrawer").evaluate((element) => {
    const rect = element.getBoundingClientRect();
    return { left: rect.left, right: rect.right };
  });
  if (drawerRect.left < 0 || drawerRect.right > metrics.viewportWidth + 1) {
    throw new Error(`${viewport.name}: memory drawer is outside viewport ${JSON.stringify(drawerRect)}`);
  }
  await page.screenshot({ path: path.join(outputDir, `ui-${viewport.name}-drawer.png`) });
  await page.click("#closeDrawer");

  await context.close();
  return { name: viewport.name, ...metrics };
}

(async () => {
  const browser = await chromium.launch({
    executablePath: edgePath,
    headless: true,
    args: ["--disable-extensions", "--no-first-run"],
  });
  try {
    const results = [];
    for (const viewport of viewports) results.push(await inspectViewport(browser, viewport));
    process.stdout.write(`${JSON.stringify(results, null, 2)}\n`);
  } finally {
    await browser.close();
  }
})().catch((error) => {
  process.stderr.write(`${error.stack || error}\n`);
  process.exit(1);
});
