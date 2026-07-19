import { chromium } from 'playwright';
import { readFileSync } from 'fs';

const htmlPath = process.argv[2];
const outputPath = process.argv[3];
// Optional 3rd arg: 'jpeg:<quality>' to trade fidelity for file size on
// photo-heavy carousels (e.g. 'jpeg:95'). Default is lossless PNG — LinkedIn's
// real cap is 100MB / 300 pages, not the 10MB soft target below, so don't
// reach for JPEG out of a mistaken size panic. Only use it if a lossless
// multi-photo carousel is landing well past ~30-40MB and you want smaller
// with negligible visible loss (stay at quality >=95 — anything lower is
// visibly worse on faces and small text, which is the whole point of this
// script existing).
const formatArg = process.argv[4] || 'png';
const [format, qualityStr] = formatArg.split(':');
const jpegQuality = qualityStr ? parseInt(qualityStr, 10) : 95;

if (!htmlPath || !outputPath) {
  console.error('Usage: node export-carousel.mjs <html-path> <pdf-output-path> [png|jpeg:<quality>]');
  process.exit(1);
}

const browser = await chromium.launch();
const page = await browser.newPage({
  viewport: { width: 1080, height: 1080 },
  deviceScaleFactor: 2,
});

await page.goto(`file://${htmlPath}`, { waitUntil: 'networkidle' });
await page.waitForTimeout(3000);

const slides = await page.$$('.slide');
const b64Images = [];

for (let i = 0; i < slides.length; i++) {
  const ext = format === 'jpeg' ? 'jpg' : 'png';
  const imgPath = `/tmp/slide-${i}.${ext}`;
  if (format === 'jpeg') {
    await slides[i].screenshot({ path: imgPath, type: 'jpeg', quality: jpegQuality });
  } else {
    await slides[i].screenshot({ path: imgPath });
  }
  b64Images.push(readFileSync(imgPath).toString('base64'));
  console.log(`Captured slide ${i + 1}`);
}

const mime = format === 'jpeg' ? 'image/jpeg' : 'image/png';
const pdfPage = await browser.newPage();
const slideHtml = b64Images.map(b64 =>
  `<div style="page-break-after:always;margin:0;padding:0;"><img src="data:${mime};base64,${b64}" style="width:1080px;height:1080px;display:block;" /></div>`
).join('');

await pdfPage.setContent(`
  <html><head><style>
    * { margin: 0; padding: 0; }
    @page { size: 1080px 1080px; margin: 0; }
  </style></head>
  <body>${slideHtml}</body></html>
`, { waitUntil: 'load' });
await pdfPage.waitForTimeout(2000);

await pdfPage.pdf({
  path: outputPath,
  width: '1080px',
  height: '1080px',
  printBackground: true,
  margin: { top: 0, right: 0, bottom: 0, left: 0 },
});

await browser.close();
console.log(`PDF saved to ${outputPath}`);
