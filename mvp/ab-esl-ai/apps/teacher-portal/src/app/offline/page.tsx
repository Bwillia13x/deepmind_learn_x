'use client';

import { WifiOff, RefreshCw, CheckCircle, Download } from 'lucide-react';

export default function OfflinePage() {
    return (
        <div className="min-h-screen bg-gray-50 flex items-center justify-center p-8">
            <div className="max-w-md w-full text-center space-y-8">
                <div className="w-24 h-24 bg-gray-100 rounded-full flex items-center justify-center mx-auto">
                    <WifiOff className="w-12 h-12 text-gray-400" />
                </div>

                <div>
                    <h1 className="text-3xl font-bold text-gray-900 mb-2">
                        You&apos;re Offline
                    </h1>
                    <p className="text-gray-500">
                        It looks like you&apos;ve lost your internet connection. Some features may be limited until you reconnect.
                    </p>
                </div>

                <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 text-left">
                    <h2 className="font-bold text-gray-900 mb-4 flex items-center gap-2">
                        <Download className="w-5 h-5 text-green-600" />
                        Available Offline
                    </h2>
                    <ul className="space-y-3">
                        {[
                            'Previously visited pages',
                            'Cached reading passages',
                            'Saved glossaries'
                        ].map((item, i) => (
                            <li key={i} className="flex items-center gap-3 text-gray-600">
                                <CheckCircle className="w-5 h-5 text-green-500 flex-shrink-0" />
                                {item}
                            </li>
                        ))}
                    </ul>
                </div>

                <button
                    onClick={() => window.location.reload()}
                    className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-4 rounded-xl transition-all shadow-sm flex items-center justify-center gap-2"
                >
                    <RefreshCw className="w-5 h-5" />
                    Try Again
                </button>
            </div>
        </div>
    );
}
