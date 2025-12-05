// Service Worker for ESL Student App
const CACHE_NAME = 'esl-student-v1';
const STATIC_CACHE = 'esl-student-static-v1';

// Static assets to cache immediately
const STATIC_ASSETS = [
    '/',
    '/dashboard',
    '/reading',
    '/speaking',
    '/vocabulary',
    '/glossary',
    '/captions',
    '/writing',
    '/vocab-lens',
    '/offline',
    '/manifest.json',
];

// Install event - cache static assets
self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(STATIC_CACHE).then((cache) => {
            console.log('[SW] Caching static assets');
            return cache.addAll(STATIC_ASSETS);
        })
    );
    self.skipWaiting();
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((cacheNames) => {
            return Promise.all(
                cacheNames
                    .filter((name) => name !== CACHE_NAME && name !== STATIC_CACHE)
                    .map((name) => {
                        console.log('[SW] Deleting old cache:', name);
                        return caches.delete(name);
                    })
            );
        })
    );
    self.clients.claim();
});

// Fetch event - network-first for API, cache-first for static
self.addEventListener('fetch', (event) => {
    const { request } = event;
    const url = new URL(request.url);

    // Skip non-GET requests
    if (request.method !== 'GET') {
        return;
    }

    // API requests: network-first with cache fallback
    if (url.pathname.startsWith('/api/')) {
        event.respondWith(
            fetch(request)
                .then((response) => {
                    // Cache successful responses
                    if (response.ok) {
                        const clone = response.clone();
                        caches.open(CACHE_NAME).then((cache) => {
                            cache.put(request, clone);
                        });
                    }
                    return response;
                })
                .catch(async () => {
                    // Return cached response if available
                    const cached = await caches.match(request);
                    if (cached) {
                        return cached;
                    }
                    // Return error response for API failures
                    return new Response(
                        JSON.stringify({ error: 'Offline', message: 'Network unavailable' }),
                        { status: 503, headers: { 'Content-Type': 'application/json' } }
                    );
                })
        );
        return;
    }

    // Static assets: cache-first with network fallback
    event.respondWith(
        caches.match(request).then((cached) => {
            if (cached) {
                // Return cached response and update cache in background
                event.waitUntil(
                    fetch(request)
                        .then((response) => {
                            if (response.ok) {
                                caches.open(STATIC_CACHE).then((cache) => {
                                    cache.put(request, response);
                                });
                            }
                        })
                        .catch(() => { })
                );
                return cached;
            }

            // Not in cache - fetch from network
            return fetch(request)
                .then((response) => {
                    // Cache successful responses
                    if (response.ok) {
                        const clone = response.clone();
                        caches.open(STATIC_CACHE).then((cache) => {
                            cache.put(request, clone);
                        });
                    }
                    return response;
                })
                .catch(() => {
                    // Return offline page for navigation requests
                    if (request.mode === 'navigate') {
                        return caches.match('/offline');
                    }
                    return new Response('Offline', { status: 503 });
                });
        })
    );
});

// Listen for messages from the app
self.addEventListener('message', (event) => {
    if (event.data === 'skipWaiting') {
        self.skipWaiting();
    }
});
