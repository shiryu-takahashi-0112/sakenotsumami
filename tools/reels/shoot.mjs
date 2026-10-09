// HTMLを指定の大きさで1枚の画像に書き出す（アイコン・OGP画像用）。
//   node shoot.mjs page.html out.png 1200 630
import { chromium } from "playwright";
import path from "node:path";
const [html, out, w, h] = process.argv.slice(2);
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
const page = await browser.newPage({ viewport: { width: +w, height: +h }, deviceScaleFactor: 1 });
await page.goto("file://" + path.resolve(html));
await page.waitForFunction(() => [...document.images].every(i => i.complete && i.naturalWidth > 0));
await page.evaluate(() => document.fonts.ready);
await page.waitForTimeout(200);
await page.screenshot({ path: out });
await browser.close();
console.log(out);
