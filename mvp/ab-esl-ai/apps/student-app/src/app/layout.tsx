import type { Metadata, Viewport } from 'next';
import { Nunito } from 'next/font/google';
import './globals.css';
import { ServiceWorkerRegistration } from '../components/ServiceWorkerRegistration';
import ErrorBoundary from '../components/ErrorBoundary';

const nunito = Nunito({ subsets: ['latin'] });

export const metadata: Metadata = {
    title: 'Alberta ESL AI - Student',
    description: 'Learning tools for ESL students',
    manifest: '/manifest.json',
    appleWebApp: {
        capable: true,
        statusBarStyle: 'default',
        title: 'ESL Student',
    },
};

export const viewport: Viewport = {
    themeColor: '#22c55e',
    width: 'device-width',
    initialScale: 1,
    maximumScale: 1,
    userScalable: false,
};

export default function RootLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <html lang="en">
            <body className={nunito.className}>
                <div className="min-h-screen bg-gradient-to-b from-green-50 to-blue-50">
                    <ErrorBoundary>
                        {children}
                    </ErrorBoundary>
                </div>
                <ServiceWorkerRegistration />
            </body>
        </html>
    );
}
