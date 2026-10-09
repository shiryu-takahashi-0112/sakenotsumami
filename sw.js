/* サケノツマミのサービスワーカー（2026-10-09）。ホーム画面に追加できるようにするために置いている。
   ページはいつもネットから取りにいき、つながらないときだけ前回開いたトップを出す（古い版が残らないように）。
   画像・データなどページ以外の読み込みには関わらない。 */
const CACHE = 'sakenotsumami-v1';

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(['./', './manifest.webmanifest', './icons/icon-192.png'])).catch(() => {}));
  self.skipWaiting();
});

self.addEventListener('activate', e => {
  e.waitUntil(caches.keys()
    .then(keys => Promise.all(keys.filter(k => k.startsWith('sakenotsumami-') && k !== CACHE).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
});

self.addEventListener('fetch', e => {
  if (e.request.mode !== 'navigate') return;
  const top = new URL('./', self.registration.scope).pathname;
  e.respondWith(
    fetch(e.request)
      .then(res => {
        if (res.ok && new URL(e.request.url).pathname === top) {
          const copy = res.clone();
          caches.open(CACHE).then(c => c.put('./', copy));
        }
        return res;
      })
      .catch(() => caches.match('./'))
  );
});
