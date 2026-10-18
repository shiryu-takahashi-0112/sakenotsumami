// サケノツマミの体感速度を測る（2026-10-13）。中くらいのスマホ（CPU 4倍遅く・Slow 4G：150ms・1.6Mbps）をまねる。
// ホームのカード・お酒のチップ・レシピ・もどる・下のタブを押してから、次の画面が描かれるまでの時間と、写真の量を出す。
//   使い方（リポジトリの外で playwright-core を入れて使う。ブラウザは Playwright の Chromium）：
//     mkdir -p /tmp/speed && cd /tmp/speed && npm i playwright-core
//     NODE_PATH=/tmp/speed/node_modules node ~/dev/sakenotsumami/tools/measure_speed.js https://osakenomitai.com/sakenotsumami/ 3
//   URL をカンマで並べると、交互に測って横に並べる（前後の比べ）。サービスワーカーは止めて測る（SW=1 で有効）。
const { chromium } = require('playwright-core');
const os = require('os');
let URL_;
const RUNS = +process.argv[3] || 3;
const fs = require('fs');
const EXE = process.env.CHROME || (() => {
  const dir = os.homedir() + '/Library/Caches/ms-playwright';
  const c = fs.readdirSync(dir).filter(d => /^chromium-\d+$/.test(d)).sort().pop();
  return `${dir}/${c}/chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing`;
})();
const NET = { offline: false, latency: 150, downloadThroughput: 1.6 * 1024 * 1024 / 8, uploadThroughput: 750 * 1024 / 8 };

async function setup(ctx) {
  const page = await ctx.newPage();
  const cdp = await ctx.newCDPSession(page);
  await cdp.send('Network.enable');
  await cdp.send('Network.emulateNetworkConditions', NET);
  await cdp.send('Emulation.setCPUThrottlingRate', { rate: 4 });
  const reqs = [];
  cdp.on('Network.responseReceived', e => reqs.push({ id: e.requestId, url: e.response.url, type: e.type, fromSW: e.response.fromServiceWorker, cache: e.response.fromDiskCache }));
  const sizes = new Map();
  cdp.on('Network.loadingFinished', e => sizes.set(e.requestId, e.encodedDataLength));
  page._reqs = reqs; page._sizes = sizes;
  await page.addInitScript(() => {
    window.__cpu = (() => { const t = performance.now(); let x = 0; for (let i = 0; i < 2e6; i++) x += i; return performance.now() - t; })();
    window.__lt = [];
    try { new PerformanceObserver(l => l.getEntries().forEach(e => window.__lt.push({ s: e.startTime, d: e.duration }))).observe({ type: 'longtask', buffered: true }); } catch (e) {}
    window.__lcp = 0;
    try { new PerformanceObserver(l => l.getEntries().forEach(e => window.__lcp = e.startTime)).observe({ type: 'largest-contentful-paint', buffered: true }); } catch (e) {}
    window.__down = 0;
    addEventListener('pointerdown', e => { window.__down = performance.now(); }, true);
  });
  return page;
}

function netSummary(page, from = 0) {
  const r = page._reqs.slice(from);
  const img = r.filter(x => x.type === 'Image');
  const kb = a => Math.round(a.reduce((s, x) => s + (page._sizes.get(x.id) || 0), 0) / 1024);
  return { reqs: r.length, kb: kb(r), imgs: img.length, imgKB: kb(img), sw: r.filter(x => x.fromSW).length };
}

// 要素をタップして、条件が満たされた最初の描画までの時間（ポインタを押した瞬間から）
async function tapUntil(page, selector, cond) {
  const el = page.locator(selector).first();
  await el.scrollIntoViewIfNeeded();
  await page.waitForTimeout(300);
  const lt0 = await page.evaluate(() => window.__lt.length);
  await page.evaluate(c => {
    window.__done = null; window.__clk = 0;
    addEventListener('click', () => { window.__clk = performance.now(); }, { capture: true, once: true });
    const f = new Function('return (' + c + ')');
    (function loop() { requestAnimationFrame(() => { if (window.__down && f()) { requestAnimationFrame(() => { window.__done = performance.now(); }); } else loop(); }); })();
  }, cond);
  const box = await el.boundingBox();
  await page.touchscreen.tap(box.x + box.width / 2, box.y + Math.min(box.height / 2, 30));
  await page.waitForFunction(() => window.__done, null, { timeout: 20000 });
  const r = await page.evaluate(lt0 => ({ ms: Math.round(window.__done - window.__down), clickDelay: Math.round(window.__clk - window.__down), longTasks: window.__lt.slice(lt0).map(x => Math.round(x.d)) }), lt0);
  return r;
}

async function run(browser, i) {
  const ctx = await browser.newContext({ serviceWorkers: process.env.SW ? 'allow' : 'block', viewport: { width: 390, height: 844 }, deviceScaleFactor: 3, isMobile: true, hasTouch: true, userAgent: 'Mozilla/5.0 (Linux; Android 13; Pixel 6a) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Mobile Safari/537.36' });
  const page = await setup(ctx);
  const out = {};
  const t0 = Date.now();
  await page.goto(URL_, { waitUntil: 'load', timeout: 120000 });
  out.loadMs = Date.now() - t0;
  await page.waitForFunction(() => document.querySelector('#todayPick .card'), null, { timeout: 60000 });
  await page.waitForTimeout(2500);
  out.cold = await page.evaluate(() => {
    const p = performance.getEntriesByName('first-contentful-paint')[0];
    return { cpu: Math.round(window.__cpu), fcp: Math.round(p ? p.startTime : -1), lcp: Math.round(window.__lcp), longTasks: window.__lt.length, longTaskMs: Math.round(window.__lt.reduce((s, x) => s + x.d, 0)) };
  });
  out.cold.net = netSummary(page);
  let n = page._reqs.length;
  // ホームの「ハイボール」カード → さがすの一覧
  out.homeChip = await tapUntil(page, '.ft-card[href="#highball"]', `!document.getElementById('viewSearch').hidden && document.querySelectorAll('#list .card').length > 0`);
  await page.waitForTimeout(3000);
  out.homeChip.net = netSummary(page, n); n = page._reqs.length;
  // さがすのお酒のチップ（ビール）
  out.chip = await tapUntil(page, '.chip[data-id="beer"]', `location.hash==='#beer' && document.querySelector('.chip.on')?.dataset.id==='beer' && document.querySelector('#count .drink-name')?.textContent==='ビール'`);
  await page.waitForTimeout(2000);
  n = page._reqs.length;
  // レシピのカード → 詳細
  out.card = await tapUntil(page, '#list .card', `document.getElementById('sheet').classList.contains('open') && document.querySelector('#detail .hero')`);
  out.card.heroMs = await page.evaluate(async () => { const t = performance.now(); const img = document.querySelector('#detail .hero'); if (!img) return -1; if (!img.complete) await new Promise(r => { img.onload = img.onerror = r; }); return Math.round(Math.max(performance.now(), t) - window.__down); });
  await page.waitForTimeout(2000);
  out.card.net = netSummary(page, n); n = page._reqs.length;
  // もどる
  out.back = await tapUntil(page, '#back', `!document.getElementById('sheet').classList.contains('open')`);
  // 下のタブ：ホーム
  out.tabHome = await tapUntil(page, '.tab[data-view="home"]', `!document.getElementById('viewHome').hidden`);
  // 下のタブ：さがす
  out.tabSearch = await tapUntil(page, '.tab[data-view="search"]', `!document.getElementById('viewSearch').hidden && document.querySelectorAll('#list .card').length > 0`);
  // 下のタブ：保存
  out.tabSaved = await tapUntil(page, '.tab[data-view="saved"]', `!document.getElementById('viewSaved').hidden`);
  // さがすを一番下までスクロールしたときの画像
  await page.evaluate(() => { location.hash = 'all'; });
  await page.waitForTimeout(1500);
  n = page._reqs.length;
  for (let y = 0; y < 40; y++) { await page.mouse.wheel(0, 1200); await page.waitForTimeout(150); }
  await page.waitForTimeout(4000);
  out.searchScroll = netSummary(page, n);
  out.totalLongTaskMs = await page.evaluate(() => Math.round(window.__lt.reduce((s, x) => s + x.d, 0)));
  // 2回目に開いたとき（キャッシュあり）
  n = page._reqs.length;
  await page.evaluate(() => { history.replaceState(null, '', location.pathname); });
  const t1 = Date.now();
  await page.reload({ waitUntil: 'load', timeout: 120000 });
  await page.waitForFunction(() => document.querySelector('#todayPick .card'), null, { timeout: 60000 });
  out.warm = { readyMs: Date.now() - t1 };
  await page.waitForTimeout(2500);
  out.warm.fcp = await page.evaluate(() => Math.round(performance.getEntriesByName('first-contentful-paint')[0]?.startTime || -1));
  out.warm.net = netSummary(page, n);
  await ctx.close();
  return out;
}

(async () => {
  const URLS = process.argv[2].split(',');
  const browser = await chromium.launch({ executablePath: EXE, headless: true });
  const res = URLS.map(() => []);
  for (let i = 0; i < RUNS; i++) for (let u = 0; u < URLS.length; u++) {
    URL_ = URLS[u];
    const r = await run(browser, i); console.error(u, JSON.stringify(r)); res[u].push(r);
  }
  await browser.close();
  const out = res.map(all => {
  const med = f => { const v = all.map(f).sort((a, b) => a - b); return v[Math.floor(v.length / 2)]; };
  return {
    'cpu check ms': med(r => r.cold.cpu),
    'cold FCP': med(r => r.cold.fcp), 'cold LCP': med(r => r.cold.lcp), 'cold load event': med(r => r.loadMs),
    'cold KB': med(r => r.cold.net.kb), 'cold imgs': med(r => r.cold.net.imgs), 'cold img KB': med(r => r.cold.net.imgKB), 'cold longtask ms': med(r => r.cold.longTaskMs),
    'tap home card→list': med(r => r.homeChip.ms), 'home card imgs after': med(r => r.homeChip.net.imgs), 'home card img KB after': med(r => r.homeChip.net.imgKB),
    'tap chip→list': med(r => r.chip.ms), 'tap recipe→sheet': med(r => r.card.ms), 'tap recipe→hero loaded': med(r => r.card.heroMs), 'detail img KB': med(r => r.card.net.imgKB),
    'tap back': med(r => r.back.ms), 'tab home': med(r => r.tabHome.ms), 'tab search': med(r => r.tabSearch.ms), 'tab saved': med(r => r.tabSaved.ms),
    'click delay': med(r => r.card.clickDelay),
    'search scroll imgs': med(r => r.searchScroll.imgs), 'search scroll img KB': med(r => r.searchScroll.imgKB),
    'session longtask ms': med(r => r.totalLongTaskMs),
    'warm ready ms': med(r => r.warm.readyMs), 'warm FCP': med(r => r.warm.fcp), 'warm KB': med(r => r.warm.net.kb), 'warm reqs from SW': med(r => r.warm.net.sw),
  };});
  console.log(JSON.stringify(out));
})();
