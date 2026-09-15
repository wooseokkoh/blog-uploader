// 앱 화면 캐시 + 갤러리 "공유"로 받은 파일 전달
const SHELL = 'shell-v2';
const SHARE = 'share-inbox';
const ASSETS = ['./', './index.html', './uploader.js', './manifest.webmanifest', './icon-192.png', './icon-512.png'];

self.addEventListener('install', (e) => {
  e.waitUntil(caches.open(SHELL).then((c) => c.addAll(ASSETS)));
  self.skipWaiting();
});

self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => k !== SHELL && k !== SHARE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim()),
  );
});

self.addEventListener('fetch', (e) => {
  const url = new URL(e.request.url);
  if (e.request.method === 'POST' && url.pathname.endsWith('/share')) {
    e.respondWith(handleShare(e.request));
    return;
  }
  if (e.request.method !== 'GET' || url.origin !== location.origin) return;
  // 네트워크 우선 → 앱을 고치면 바로 반영, 오프라인이면 캐시
  e.respondWith(
    fetch(e.request)
      .then((res) => {
        const copy = res.clone();
        caches.open(SHELL).then((c) => c.put(e.request, copy));
        return res;
      })
      .catch(() => caches.match(e.request, { ignoreSearch: true })),
  );
});

async function handleShare(request) {
  const form = await request.formData();
  const files = form.getAll('media').filter((f) => typeof f === 'object');
  const cache = await caches.open(SHARE);
  for (const k of await cache.keys()) await cache.delete(k);
  await Promise.all(files.map((f, i) => cache.put(`./shared/${i}`, new Response(f, {
    headers: { 'Content-Type': f.type || 'application/octet-stream', 'X-File-Name': encodeURIComponent(f.name) },
  }))));
  return Response.redirect(new URL(`./?shared=${files.length}`, self.registration.scope).href, 303);
}
