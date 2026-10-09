// HTMLを指定の大きさで1枚の画像に書き出す（アイコン・OGP画像用）。
//   node shoot.mjs page.html out.png 1200 630
import { chromium } from "playwright";
import path from "node:path";
const [html, out, w, h] = process.argv.slice(2);
// Mac では入っている Google Chrome を使う。クラウド（Linux）では playwright の chromium を使う（npx playwright install chromium）。
// PLAYWRIGHT_CHANNEL で上書きできる（空文字なら同梱の chromium）。
const channel = process.env.PLAYWRIGHT_CHANNEL ?? (process.platform === "darwin" ? "chrome" : "");
const browser = await chromium.launch(channel ? { channel } : {});
const page = await browser.newPage({ viewport: { width: +w, height: +h }, deviceScaleFactor: 1 });
await page.goto("file://" + path.resolve(html));
await page.waitForFunction(() => [...document.images].every(i => i.complete && i.naturalWidth > 0));
await page.evaluate(() => document.fonts.ready);
await page.waitForTimeout(200);
await page.screenshot({ path: out });
await browser.close();
console.log(out);
