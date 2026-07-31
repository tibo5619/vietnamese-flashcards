// Minimal service worker: caches the app shell so it's installable as a PWA
// and still opens (from cache) when offline.
// Network-first: every request tries the network first (so app updates
// pushed to GitHub Pages are picked up as soon as there's a connection) and
// only falls back to the cached copy when the network is unavailable.
const CACHE_NAME = 'nhat-chu-v8';
const ASSETS = [
  './',
  './index.html',
  './manifest.json',
  './data/connect1.json',
  './data/connect2.json',
  './data/dictionary.json',
  './icons/icon-192.png',
  './icons/icon-512.png',
  './icons/icon-maskable-192.png',
  './icons/icon-maskable-512.png'
];

self.addEventListener('install', (event) => {
  event.waitUntil(caches.open(CACHE_NAME).then((cache) => cache.addAll(ASSETS)));
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k)))
    )
  );
  self.clients.claim();
});

self.addEventListener('fetch', (event) => {
  if (event.request.method !== 'GET') return;
  event.respondWith(
    fetch(event.request)
      .then((response) => {
        const copy = response.clone();
        caches.open(CACHE_NAME).then((cache) => cache.put(event.request, copy)).catch(() => {});
        return response;
      })
      .catch(() => caches.match(event.request))
  );
});
