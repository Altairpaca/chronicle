const cacheName = 'chronicle-v1';
const files = ['/', '/styles.css', '/components.css', '/app.js', '/manifest.webmanifest'];
self.addEventListener('install', (event) => event.waitUntil(caches.open(cacheName).then((cache) => cache.addAll(files))));
self.addEventListener('fetch', (event) => { if (event.request.method === 'GET' && !event.request.url.includes('/api/')) event.respondWith(caches.match(event.request).then((hit) => hit || fetch(event.request))); });
