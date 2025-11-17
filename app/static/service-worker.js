const VERSION = 'pwa-initial';

self.addEventListener('install', (event) => {
    self.skipWaiting();
});

self.addEventListener('activate', (event) => {
    event.waitUntil(self.clients.claim());
});

self.addEventListener('fetch', () => {
    // 캐시 기능 없이 네트워크 요청만 통과
});

