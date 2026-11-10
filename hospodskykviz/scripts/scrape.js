const { chromium } = require('playwright');
const fs = require('fs');
const [,, profileUrl, tag, maxQuizzes = '70', withDiff = '1'] = process.argv;
const sleep = ms => new Promise(r => setTimeout(r, ms));
const lw = (p, act) => Promise.all([p.waitForResponse(r => r.url().includes('/livewire/update'), { timeout: 30000 }), act()]).then(() => sleep(350));
const rowsFn = () => [...document.querySelectorAll('main table tbody tr')].map(tr => [...tr.children].map(td => td.innerText.trim()).concat([[...tr.querySelectorAll('a')].map(a => a.href).filter(h => h.includes('odehrane-kvizy'))[0] || '', tr.querySelector('.answer') ? tr.querySelector('.answer').className : '']));
(async () => {
  const b = await chromium.launch({ proxy: { server: process.env.HTTPS_PROXY } });
  const ctx = await b.newContext();
  await ctx.route(/google|doubleclick|facebook|tiktok|typekit|gtm/, r => r.abort());
  const p = await ctx.newPage();
  const listFile = `data/${tag}_list.json`;
  let list = fs.existsSync(listFile) ? JSON.parse(fs.readFileSync(listFile)) : null;
  if (!list) {
    list = [];
    await p.goto(profileUrl, { waitUntil: 'networkidle', timeout: 90000 });
    await lw(p, () => p.locator('select[title="Počet položek na stránku"]').selectOption('36'));
    for (let pg = 1; list.length < +maxQuizzes; pg++) {
      if (pg > 1) { const nx = p.locator(`[wire\\:click="gotoPage(${pg}, 'page')"]`).first(); if (!await nx.count()) break; await lw(p, () => nx.click()); }
      const rows = await p.evaluate(rowsFn);
      for (const r of rows) if (r[5]) list.push({ rank: r[0], date: r[1], pub: r[2], pts: r[3], url: r[5] });
    }
    list = list.slice(0, +maxQuizzes);
    fs.writeFileSync(listFile, JSON.stringify(list, null, 1));
  }
  console.log('quizzes', list.length);
  for (const q of list) {
    const id = q.url.split('/').pop(), f = `data/${tag}_${id}.json`;
    if (fs.existsSync(f)) continue;
    try {
      await p.goto(q.url, { waitUntil: 'networkidle', timeout: 90000 });
      await lw(p, () => p.locator('select[title="Počet položek na stránku"]').selectOption('30'));
      const out = [];
      for (let pg = 1; pg <= 2; pg++) {
        if (pg > 1) { const nx = p.locator(`[wire\\:click="gotoPage(${pg}, 'page')"]`).first(); if (!await nx.count()) break; await lw(p, () => nx.click()); }
        const n = await p.locator('[wire\\:click^="toggleDetail"]').count();
        const rows = (await p.evaluate(rowsFn)).filter(r => /^\d+\.$/.test(r[0]));
        for (let i = 0; i < rows.length; i++) {
          const r = rows[i]; const o = { n: r[0], q: r[1], a: r[2], pts: r[3], cls: r[6] };
          if (withDiff === '1' && i < n) {
            await lw(p, () => p.locator('[wire\\:click^="toggleDetail"]').nth(i).click());
            o.diff = await p.evaluate(() => { const d = document.querySelector('main .item-detail-content, main .challenge-table'); return d ? d.innerText.replace(/\s+/g, ' ').trim() : null; });
          }
          out.push(o);
        }
      }
      fs.writeFileSync(f, JSON.stringify({ ...q, rows: out }, null, 1));
      console.log(q.date, q.pub, out.length);
    } catch (e) { console.log('ERR', q.date, e.message.slice(0, 150)); }
  }
  await b.close();
})();
