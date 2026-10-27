// Offline cache for the app shell and category packs requested by the learner.
const CACHE = 'marathi-cards-v5';
const SHELL = ['./', './index.html', './data/manifest.json', './manifest.webmanifest', './icons/icon-192.png', './icons/icon-512.png', './icons/apple-touch-icon.png'];

self.addEventListener('install', (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(SHELL)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', (e) => {
  e.waitUntil(caches.keys().then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k)))).then(() => self.clients.claim()));
});

self.addEventListener('fetch', (e) => {
  const url = new URL(e.request.url);
  if (url.origin !== location.origin) return;
  // Refresh the small manifest in the background; category packs load and cache only when requested.
  if (url.pathname.endsWith('/data/manifest.json')) {
    const refresh = fetch(e.request).then((response) => {
      if (response.ok) caches.open(CACHE).then((cache) => cache.put(e.request, response.clone()));
      return response;
    });
    e.waitUntil(refresh.catch(() => {}));
    e.respondWith(caches.match(e.request).then((cached) => cached || refresh));
    return;
  }
  if (url.pathname.includes('/data/')) {
    e.respondWith(caches.match(e.request).then((hit) => hit || fetch(e.request).then((response) => {
      if (response.ok) caches.open(CACHE).then((cache) => cache.put(e.request, response.clone()));
      return response;
    })));
    return;
  }
  e.respondWith(caches.match(e.request).then((hit) => hit || fetch(e.request)));
});
