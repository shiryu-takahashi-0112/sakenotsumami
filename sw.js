/* サケノツマミのサービスワーカー（2026-10-09 に作り、2026-10-13 に表示を速くするためのキャッシュを足した）。
   - ページ（HTML）：いつもネットから取りにいき、つながらないときだけ前回開いたトップを出す（更新がすぐ届くように）。
   - 写真（images/・icons/）：一度読んだものは、端末に置いたものをすぐ出す。7日たったものは、出したあとで裏で取り直す。
     置いておくのは新しい順に 600 枚まで。
   - レシピのデータ・画面の部品（.js・.css・.json）：端末に置いたものをすぐ出し、裏で新しいものを取って次に備える。
     index.html は recipes.js?v=<中身のハッシュ> のように読むので（tools/build_pages.py が付ける）、
     公開してページが新しくなれば、新しいファイルを取りにいく。
   ほかのサイト（Firebase・書体・アイコン）の読み込みには関わらない。 */
const PAGE = 'sakenotsumami-page-v2';
const ASSET = 'sakenotsumami-asset-v2';
const IMG = 'sakenotsumami-img-v1';
const KEEP = [PAGE, ASSET, IMG];
const IMG_MAX = 600;
const IMG_REFRESH = 7 * 864e5;
const SCOPE = new URL('./', self.registration.scope).pathname;

self.addEventListener('install', e => {
  e.waitUntil(caches.open(PAGE).then(c => c.addAll(['./', './manifest.webmanifest', './icons/icon-192.png'])).catch(() => {}));
  self.skipWaiting();
});

self.addEventListener('activate', e => {
  e.waitUntil(caches.keys()
    .then(keys => Promise.all(keys.filter(k => k.startsWith('sakenotsumami-') && !KEEP.includes(k)).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
});

self.addEventListener('fetch', e => {
  const req = e.request;
  if(req.method !== 'GET') return;
  if(req.mode === 'navigate') return e.respondWith(page(req));
  const url = new URL(req.url);
  if(url.origin !== self.location.origin || !url.pathname.startsWith(SCOPE)) return;
  const path = url.pathname.slice(SCOPE.length);
  if(/^(images|icons)\/.+\.(webp|jpe?g|png|svg)$/.test(path)) return e.respondWith(image(req, e));
  if(/\.(js|css|json|webmanifest)$/.test(path) && path !== 'sw.js') return e.respondWith(asset(req, e));
});

// ページ：ネットを先に。つながらないときだけ前回のトップ
function page(req){
  return fetch(req)
    .then(res => {
      if(res.ok && new URL(req.url).pathname === SCOPE){
        const copy = res.clone();
        caches.open(PAGE).then(c => c.put('./', copy));
      }
      return res;
    })
    .catch(() => caches.match('./'));
}

const ok = res => res && res.ok && res.type === 'basic';

// 写真：端末に置いたものを先に
async function image(req, e){
  const cache = await caches.open(IMG);
  const hit = await cache.match(req);
  const refresh = () => fetch(req).then(res => {
    if(ok(res)) e.waitUntil(cache.put(req, res.clone()).then(() => trim(cache)));
    return res;
  });
  if(hit){
    const at = Date.parse(hit.headers.get('date') || '') || 0;
    if(Date.now() - at > IMG_REFRESH) e.waitUntil(refresh().catch(() => {}));
    return hit;
  }
  return refresh();
}

async function trim(cache){
  const keys = await cache.keys();
  for(let i = 0; i < keys.length - IMG_MAX; i++) await cache.delete(keys[i]);
}

// データ・部品：端末に置いたものをすぐ出し、裏で取り直す。同じファイルの古い版（?v= が違うもの）は消す
async function asset(req, e){
  const cache = await caches.open(ASSET);
  const hit = await cache.match(req);
  const net = fetch(req).then(async res => {
    if(ok(res)){
      await cache.put(req, res.clone());
      const path = new URL(req.url).pathname;
      for(const k of await cache.keys()){
        if(new URL(k.url).pathname === path && k.url !== req.url) await cache.delete(k);
      }
    }
    return res;
  });
  if(hit){
    e.waitUntil(net.catch(() => {}));
    return hit;
  }
  return net;
}
