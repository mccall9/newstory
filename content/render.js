const { chromium } = require("playwright");
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1200, height: 1400 } });
  await p.goto("file://" + process.cwd() + "/" + process.argv[2]);
  await p.addStyleTag({ content: ".s{transform:none!important;margin:0!important}" });
  await p.waitForLoadState("networkidle");
  await p.evaluate(() => document.fonts.ready);
  const overflow = await p.evaluate(() =>
    [...document.querySelectorAll(".content,.cta,.cover-text,.pad,.news,.task")].map((el) => {
      const s = el.closest(".s").id;
      const r = el.getBoundingClientRect(), sr = el.closest(".s").getBoundingClientRect();
      return { s, over: el.scrollHeight - el.clientHeight, bottomGap: Math.round(sr.bottom - r.bottom), contentBottom: Math.round([...el.children].reduce((m, c) => Math.max(m, c.getBoundingClientRect().bottom), 0) - sr.top) };
    }));
  console.log(JSON.stringify(overflow));
  const n = await p.locator(".s").count();
  for (let i = 1; i <= n; i++) await p.locator(`#slide-${i}`).screenshot({ path: `${process.argv[3] || "slide"}-${i}.jpg`, type: "jpeg", quality: 92 });
  await b.close();
})();
