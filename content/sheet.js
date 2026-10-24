const { chromium } = require("playwright"); const fs = require("fs");
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1400, height: 900 } });
  const [pre, n] = [process.argv[2], +process.argv[3]];
  const imgs = [...Array(n)].map((_, i) => `<img src="data:image/jpeg;base64,${fs.readFileSync(`${pre}-${i + 1}.jpg`).toString("base64")}" style="width:340px">`).join("");
  await p.setContent(`<body style="margin:0;background:#333;display:flex;flex-wrap:wrap;gap:6px;padding:6px">${imgs}</body>`);
  await p.screenshot({ path: `${pre}-sheet.png`, fullPage: true }); await b.close();
})();
