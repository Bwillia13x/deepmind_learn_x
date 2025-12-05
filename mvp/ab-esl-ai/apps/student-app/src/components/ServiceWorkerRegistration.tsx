'use client';

import { useEffect, useState } from 'react';

export function ServiceWorkerRegistration() {
    const [updateAvailable, setUpdateAvailable] = useState(false);

    useEffect(() => {
        if (typeof window === 'undefined' || !('serviceWorker' in navigator)) {
            return;
        }

        const registerSW = async () => {
            try {
                const registration = await navigator.serviceWorker.register('/sw.js');
                console.log('Service Worker registered:', registration.scope);

                // Check for updates
                registration.addEventListener('updatefound', () => {
                    const newWorker = registration.installing;
                    if (newWorker) {
                        newWorker.addEventListener('statechange', () => {
                            if (
                                newWorker.state === 'installed' &&
                                navigator.serviceWorker.controller
                            ) {
                                setUpdateAvailable(true);
                            }
                        });
                    }
                });

                // Check for updates periodically
                setInterval(() => {
                    registration.update();
                }, 60 * 60 * 1000); // Every hour
            } catch (error) {
                console.error('Service Worker registration failed:', error);
            }
        };

        registerSW();
    }, []);

    const handleUpdate = () => {
        if ('serviceWorker' in navigator && navigator.serviceWorker.controller) {
            navigator.serviceWorker.controller.postMessage('skipWaiting');
            window.location.reload();
        }
    };

    if (!updateAvailable) {
        return null;
    }

    return (
        <div className="fixed bottom-4 left-4 right-4 bg-primary-600 text-white p-4 rounded-xl shadow-lg z-50 animate-fadeIn">
            <div className="flex items-center justify-between">
                <span>A new version is available!</span>
                <button
                    onClick={handleUpdate}
                    className="bg-white text-primary-600 font-bold px-4 py-2 rounded-lg"
                >
                    Update
                </button>
            </div>
        </div>
    );
}
