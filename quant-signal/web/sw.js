/* 앱 껍데기만 캐시한다. signals.json 은 항상 네트워크에서 받는다 —
   낡은 시그널을 보여 주는 것은 안 보여 주는 것보다 나쁘다. */
const CACHE = 'quant-signal-v1';
const SHELL = ['./', './index.html', './app.js', './manifest.webmanifest'];

self.addEventListener('install', (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(SHELL)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (e) => {
  const url = new URL(e.request.url);
  if (e.request.method !== 'GET' || url.origin !== self.location.origin) return;
  if (url.pathname.endsWith('signals.json')) return;  // 항상 최신으로
  e.respondWith(caches.match(e.request).then((hit) => hit || fetch(e.request)));
});
