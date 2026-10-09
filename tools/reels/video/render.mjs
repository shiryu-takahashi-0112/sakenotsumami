// リールのHTMLを1コマずつ撮ってPNGに書き出す（macrohack-cowork/video/render.mjs と同じ作り方）。
//   node video/render.mjs <page.html> <出力フォルダ>              … 全コマ（30fps）と timeline.json
//   node video/render.mjs <page.html> <出力フォルダ> 1.0 4.2 …    … 指定した秒だけ t<秒>.png に書き出す（確認用）
// ページ側に window.prepare()（フォント読み込み→配置）と window.render(t) が必要。
import { chromium } from "playwright";
import fs from "node:fs";
import path from "node:path";

const FPS = 30;
const [html, out, ...times] = process.argv.slice(2);
if (!html || !out) { console.error("使い方: node video/render.mjs <page.html> <出力フォルダ> [秒 …]"); process.exit(1); }

// Mac では入っている Google Chrome を使う。クラウド（Linux）では playwright の chromium を使う（npx playwright install chromium）。
// PLAYWRIGHT_CHANNEL で上書きできる（空文字なら同梱の chromium）。
const channel = process.env.PLAYWRIGHT_CHANNEL ?? (process.platform === "darwin" ? "chrome" : "");
// クラウドの環境には、決まった版の Chromium が /opt/pw-browsers に最初から入っていて、新しい版は取りに行けない
// （cdn.playwright.dev が通信の許可に無い。2026-10-09 の試験で確認）。
// そのため、PW_EXECUTABLE か、/opt/pw-browsers の中にある Chromium があれば、それを使う。
import { existsSync, readdirSync } from "node:fs";
function bundledChromium() {
  if (process.env.PW_EXECUTABLE) return process.env.PW_EXECUTABLE;
  const root = process.env.PLAYWRIGHT_BROWSERS_PATH || "/opt/pw-browsers";
  if (!existsSync(root)) return "";
  const dirs = readdirSync(root).filter((d) => /^chromium-\d+$/.test(d)).sort((a, b) => Number(b.split("-")[1]) - Number(a.split("-")[1]));
  for (const d of dirs) {
    for (const p of [`${root}/${d}/chrome-linux/chrome`, `${root}/${d}/chrome-linux64/chrome`]) if (existsSync(p)) return p;
  }
  return "";
}
const exe = channel ? "" : bundledChromium();
const browser = await chromium.launch(channel ? { channel } : exe ? { executablePath: exe } : {});
try {
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  const errors = [];
  page.on("pageerror", e => errors.push(String(e)));
  page.on("requestfailed", r => errors.push("読み込み失敗: " + r.url()));
  await page.goto("file://" + path.resolve(html));
  // 画像がすべて読み込まれるまで待つ
  await page.waitForFunction(() => [...document.images].every(i => i.complete && i.naturalWidth > 0), null, { timeout: 20000 });
  await page.evaluate(() => Promise.all([...document.images].map(i => i.decode())));
  // フォントを読み込んで配置を決める
  const tl = await page.evaluate(() => window.prepare());
  await page.waitForTimeout(150);
  if (errors.length) throw new Error(errors.join("\n"));

  fs.mkdirSync(out, { recursive: true });
  if (times.length) {
    for (const t of times.map(Number)) {
      await page.evaluate(t => window.render(t), t);
      const p = path.join(out, `t${t.toFixed(2)}.png`);
      await page.screenshot({ path: p });
      console.log(p);
    }
  } else {
    for (const f of fs.readdirSync(out)) if (f.endsWith(".png")) fs.rmSync(path.join(out, f));
    const total = Math.round(tl.duration * FPS);
    for (let i = 0; i < total; i++) {
      await page.evaluate(t => window.render(t), i / FPS);
      await page.screenshot({ path: path.join(out, `${String(i).padStart(4, "0")}.png`) });
    }
    fs.writeFileSync(path.join(out, "timeline.json"), JSON.stringify({ ...tl, frames: total, fps: FPS }));
    console.log(JSON.stringify(tl));
  }
} finally {
  await browser.close();
}
