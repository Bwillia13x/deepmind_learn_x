'use client';

export default function OfflinePage() {
    return (
        <main className="min-h-screen flex items-center justify-center p-6 bg-[radial-gradient(circle_at_center,_var(--tw-gradient-stops))] from-gray-100 via-white to-gray-50">
            <div className="text-center max-w-lg w-full bg-white/80 backdrop-blur-md rounded-[2.5rem] shadow-2xl p-10 border border-white/50 animate-in zoom-in duration-500">
                <div className="text-8xl mb-8 animate-bounce">📵</div>
                <h1 className="text-4xl font-bold text-gray-800 mb-4">
                    You&apos;re Offline
                </h1>
                <p className="text-xl text-gray-600 mb-8 leading-relaxed">
                    It looks like you&apos;re not connected to the internet.
                    Some features won&apos;t work until you&apos;re back online.
                </p>
                <div className="space-y-6 mb-8">
                    <p className="text-sm font-bold text-gray-500 uppercase tracking-wider">
                        While offline, you can still:
                    </p>
                    <ul className="text-left text-gray-700 space-y-3 bg-gray-50/80 p-6 rounded-[2rem] border border-gray-100">
                        <li className="flex items-center gap-3 text-lg font-medium">
                            <span className="text-2xl">📝</span> Practice vocabulary flashcards
                        </li>
                        <li className="flex items-center gap-3 text-lg font-medium">
                            <span className="text-2xl">📖</span> Read cached stories
                        </li>
                    </ul>
                </div>
                <button
                    onClick={() => window.location.reload()}
                    className="w-full bg-gray-800 hover:bg-gray-900 text-white font-bold py-4 px-8 rounded-2xl transition-all hover:scale-105 shadow-lg text-lg"
                >
                    Try Again
                </button>
            </div>
        </main>
    );
}
