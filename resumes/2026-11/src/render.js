// Usage: node render.js in.html out.pdf [out.png]
const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const [inp, out, png] = process.argv.slice(2);
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto('file://' + path.resolve(inp));
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(300);
  await page.pdf({ path: out, format: 'A4', preferCSSPageSize: true, printBackground: true });
  // report content height vs one A4 page (297mm minus margins 21mm => 276mm ~ 1043px at 96dpi)
  const h = await page.evaluate(() => document.body.scrollHeight);
  console.log('content height px:', h, '(one page fits <= ~1043px at A4 width minus margins)');
  if (png) {
    await page.emulateMedia({ media: 'print' });
    await page.setViewportSize({ width: 794, height: 1123 });
    await page.screenshot({ path: png, fullPage: true });
  }
  await browser.close();
})();
