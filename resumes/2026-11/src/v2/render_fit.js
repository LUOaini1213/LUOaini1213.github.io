// Auto-fit renderer: finds the largest font size (--fs) and section spacing (--gap)
// that keep the CV on exactly one A4 page, then writes PDF + PNG preview.
// Usage: node render_fit.js <in.html> [--min 9.6] [--max 11.2]
// Prints a JSON report: { fs, gap, fill, pages, status }.
//   status "ok"         -> one page, fill >= 0.96, fs within [min, max]
//   status "overflow"   -> does not fit even at --min font: cut content
//   status "underfill"  -> page still emptier than 96% at --max font and max gap: add content
const { chromium } = require('playwright');
const path = require('path');
const { execFileSync } = require('child_process');

const args = process.argv.slice(2);
const inp = args[0];
const opt = (k, d) => { const i = args.indexOf(k); return i >= 0 ? parseFloat(args[i + 1]) : d; };
const MIN = opt('--min', 9.6), MAX = opt('--max', 11.2);
const MM = 96 / 25.4;
const AVAIL = (297 - 11 - 10) * MM;        // printable height in CSS px (must match cv2.css @page margins)
const WIDTH = Math.round((210 - 26) * MM); // printable width in CSS px
const SAFE = 0.985;                        // keep a small safety margin against print/screen differences

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: WIDTH, height: 1200 } });
  await page.emulateMedia({ media: 'print' });
  await page.goto('file://' + path.resolve(inp));
  await page.evaluate(() => document.fonts.ready);
  const measure = (fs, gap) => page.evaluate(([fs, gap]) => {
    const r = document.documentElement;
    r.style.setProperty('--fs', fs + 'pt');
    r.style.setProperty('--gap', gap + 'pt');
    return document.body.scrollHeight;
  }, [fs, gap]);
  await page.waitForTimeout(150);

  // 1) largest font that fits with a modest gap
  const GAP0 = 4;
  let fs = null;
  for (let f = MAX; f >= MIN - 1e-9; f = Math.round((f - 0.1) * 10) / 10) {
    if (await measure(f, GAP0) <= AVAIL * SAFE) { fs = f; break; }
  }
  let status = 'ok';
  if (fs === null) { fs = MIN; status = 'overflow'; }
  // 2) grow gap to fill the page
  let gap = GAP0;
  if (status === 'ok') {
    for (let g = GAP0; g <= 11; g = Math.round((g + 0.25) * 100) / 100) {
      if (await measure(fs, g) <= AVAIL * SAFE) gap = g; else break;
    }
  }
  let h = await measure(fs, gap);
  const out = inp.replace(/\.html$/, '.pdf');
  const pdfOnce = async () => {
    await page.pdf({ path: out, preferCSSPageSize: true, printBackground: true });
    return parseInt(execFileSync('pdfinfo', [out]).toString().match(/Pages:\s+(\d+)/)[1], 10);
  };
  let pages = await pdfOnce();
  // safety: if the printed PDF spills, back off gap then font
  while (pages > 1 && (gap > GAP0 || fs > MIN)) {
    if (gap > GAP0) gap = Math.max(GAP0, gap - 0.5); else fs = Math.round((fs - 0.1) * 10) / 10;
    h = await measure(fs, gap);
    pages = await pdfOnce();
  }
  if (pages > 1) status = 'overflow';
  const fill = h / AVAIL;
  if (status === 'ok' && fs >= MAX - 1e-9 && fill < 0.96) status = 'underfill';
  const png = inp.replace(/\.html$/, '');
  execFileSync('pdftoppm', ['-r', '80', '-png', '-singlefile', out, png]);
  console.log(JSON.stringify({ file: out, preview: png + '.png', fs, gap, fill: Math.round(fill * 1000) / 1000, pages, status }));
  await browser.close();
})();
