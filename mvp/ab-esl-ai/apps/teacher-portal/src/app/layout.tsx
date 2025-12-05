import type { Metadata, Viewport } from 'next';
import { Inter } from 'next/font/google';
import Link from 'next/link';
import './globals.css';
import { ServiceWorkerRegistration } from '../components/ServiceWorkerRegistration';
import ErrorBoundary from '../components/ErrorBoundary';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'Alberta ESL AI - Teacher Portal',
  description: 'AI-powered tools for ESL teachers in Alberta schools',
  manifest: '/manifest.json',
  appleWebApp: {
    capable: true,
    statusBarStyle: 'default',
    title: 'ESL Teacher',
  },
  formatDetection: {
    telephone: false,
  },
};

export const viewport: Viewport = {
  themeColor: '#2563eb',
  width: 'device-width',
  initialScale: 1,
  maximumScale: 1,
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <div className="min-h-screen bg-gray-50">
          <nav className="bg-white border-b border-gray-200 sticky top-0 z-50 backdrop-blur-lg bg-white/80">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              <div className="flex justify-between h-16">
                <div className="flex items-center">
                  <Link href="/" className="flex items-center group">
                    <span className="text-2xl mr-2 group-hover:scale-110 transition-transform">🍁</span>
                    <span className="text-xl font-bold text-gray-900 group-hover:text-indigo-600 transition-colors">
                      Alberta ESL AI
                    </span>
                    <span className="ml-2 text-xs font-medium text-indigo-600 bg-indigo-50 px-2 py-0.5 rounded-full border border-indigo-100">
                      Teacher
                    </span>
                  </Link>
                </div>
                <div className="hidden md:flex items-center space-x-1">
                  {[
                    ['Home', '/'],
                    ['Leveler', '/leveler'],
                    ['Decodable', '/decodable'],
                    ['Reading', '/reading'],
                    ['Curriculum', '/curriculum'],
                    ['L1 Transfer', '/l1-transfer'],
                    ['Glossary', '/glossary'],
                    ['Analytics', '/analytics'],
                  ].map(([label, href]) => (
                    <Link
                      key={href}
                      href={href}
                      className="text-gray-600 hover:text-indigo-600 hover:bg-indigo-50 px-3 py-2 rounded-md text-sm font-medium transition-colors"
                    >
                      {label}
                    </Link>
                  ))}
                </div>
              </div>
            </div>
          </nav>
          <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <ErrorBoundary>
              {children}
            </ErrorBoundary>
          </main>
        </div>
        <ServiceWorkerRegistration />
      </body>
    </html>
  );
}
