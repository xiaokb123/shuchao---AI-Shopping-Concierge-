// Service Worker 版本
const CACHE_VERSION = 'v2';
const CACHE_NAME = `shuchao-${CACHE_VERSION}`;

// 需要缓存的资源列表
const urlsToCache = [
    '/static/css/style.css',
    '/static/js/main.js',
    '/static/js/auth.js',
    'https://cdn.bootcdn.net/ajax/libs/twitter-bootstrap/5.3.0/css/bootstrap.min.css',
    'https://cdn.bootcdn.net/ajax/libs/twitter-bootstrap/5.3.0/js/bootstrap.bundle.min.js'
];

// 安装Service Worker
self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => {
                console.log('Opened cache');
                return cache.addAll(urlsToCache);
            })
    );
    self.skipWaiting();
});

// 激活Service Worker
self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys().then(cacheNames => {
            return Promise.all(
                cacheNames.map(cacheName => {
                    if (cacheName !== CACHE_NAME) {
                        return caches.delete(cacheName);
                    }
                })
            );
        })
    );
    self.clients.claim();
});

// 处理请求
self.addEventListener('fetch', event => {
    const acceptHeader = event.request.headers.get('accept') || '';
    if (acceptHeader.indexOf('text/html') > -1) {
        // For HTML requests, always try network first
        event.respondWith(
            fetch(event.request)
                .catch(() => caches.match(event.request))
        );
    } else {
        // For non-HTML requests, use network-first with cache fallback
        event.respondWith(
            fetch(event.request)
                .then(response => {
                    if (response && response.status === 200 && event.request.method === 'GET') {
                        const responseClone = response.clone();
                        caches.open(CACHE_NAME)
                            .then(cache => {
                                cache.put(event.request, responseClone);
                            });
                    }
                    return response;
                })
                .catch(() => caches.match(event.request))
        );
    }
}); 