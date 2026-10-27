// Offline cache so the home-screen app opens without network; words.json is refreshed from the network when available.
const CACHE = 'marathi-cards-v4';
const SHELL = ['./', './index.html', './words.json', './manifest.webmanifest', './icons/icon-192.png', './icons/icon-512.png', './icons/apple-touch-icon.png'];

self.addEventListener('install', (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(SHELL)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', (e) => {
  e.waitUntil(caches.keys().then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k)))).then(() => self.clients.claim()));
});

self.addEventListener('fetch', (e) => {
  const url = new URL(e.request.url);
  if (url.origin !== location.origin) return;
  // Show the cached deck immediately, then refresh it in the background for the next visit.
  if (url.pathname.endsWith('words.json')) {
    const refresh = fetch(e.request).then((response) => {
      if (response.ok) caches.open(CACHE).then((cache) => cache.put(e.request, response.clone()));
      return response;
    });
    e.waitUntil(refresh.catch(() => {}));
    e.respondWith(caches.match(e.request).then((cached) => cached || refresh));
    return;
  }
  e.respondWith(caches.match(e.request).then((hit) => hit || fetch(e.request)));
});
