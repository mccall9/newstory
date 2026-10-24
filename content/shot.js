// Screenshot de uma página-guia em tamanho de celular: node shot.js <arquivo-ou-url> <saida.png>
const { chromium } = require("playwright");
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 3, colorScheme: "light" });
  const src = process.argv[2];
  await p.goto(src.startsWith("http") ? src : "file://" + src);
  await p.waitForLoadState("networkidle");
  await p.evaluate(() => document.fonts.ready);
  await p.screenshot({ path: process.argv[3] });
  await b.close();
})();
