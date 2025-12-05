'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';

interface SessionData {
    token: string;
    sessionId: number;
    participantId: number;
    nickname: string;
    l1: string;
}

export default function DashboardPage() {
    const router = useRouter();
    const [session, setSession] = useState<SessionData | null>(null);

    useEffect(() => {
        const stored = localStorage.getItem('session');
        if (!stored) {
            router.push('/');
            return;
        }
        setSession(JSON.parse(stored));
    }, [router]);

    const handleLeave = () => {
        localStorage.removeItem('session');
        router.push('/');
    };

    if (!session) {
        return (
            <div className="min-h-screen flex items-center justify-center">
                <div className="animate-pulse text-2xl">Loading...</div>
            </div>
        );
    }

    const activities = [
        {
            href: '/captions',
            emoji: '🎤',
            title: 'Live Captions',
            description: 'See your teacher\'s words on screen',
            color: 'bg-indigo-500 hover:bg-indigo-600',
        },
        {
            href: '/reading',
            emoji: '📖',
            title: 'Reading Practice',
            description: 'Read aloud and check your fluency',
            color: 'bg-blue-500 hover:bg-blue-600',
        },
        {
            href: '/speaking',
            emoji: '🗣️',
            title: 'Speaking Practice',
            description: 'Practice pronunciation',
            color: 'bg-green-500 hover:bg-green-600',
        },
        {
            href: '/vocabulary',
            emoji: '📝',
            title: 'Vocabulary',
            description: 'Learn new words',
            color: 'bg-purple-500 hover:bg-purple-600',
        },
        {
            href: '/glossary',
            emoji: '🌍',
            title: 'My Language',
            description: 'See words in your language',
            color: 'bg-orange-500 hover:bg-orange-600',
        },
        {
            href: '/writing',
            emoji: '✏️',
            title: 'Writing Helper',
            description: 'Get help with your writing',
            color: 'bg-pink-500 hover:bg-pink-600',
        },
        {
            href: '/vocab-lens',
            emoji: '📸',
            title: 'Vocab Lens',
            description: 'Point camera to learn words',
            color: 'bg-cyan-500 hover:bg-cyan-600',
        },
    ];

    return (
        <main className="min-h-screen p-4 md:p-8">
            {/* Header */}
            <header className="max-w-4xl mx-auto flex items-center justify-between mb-8 bg-white p-6 rounded-3xl shadow-sm border border-white/50 backdrop-blur-sm">
                <div>
                    <h1 className="text-3xl font-black text-gray-800 mb-1">
                        Hello, {session.nickname}! 👋
                    </h1>
                    <p className="text-gray-500 font-medium text-lg">What would you like to practice today?</p>
                </div>
                <button
                    onClick={handleLeave}
                    className="text-gray-500 hover:text-red-500 px-4 py-2 rounded-xl
                     hover:bg-red-50 transition-colors font-bold flex items-center gap-2"
                >
                    <span>Leave</span>
                    <span>🚪</span>
                </button>
            </header>

            {/* Activity Cards */}
            <div className="max-w-4xl mx-auto grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
                {activities.map((activity) => (
                    <Link
                        key={activity.href}
                        href={activity.href}
                        className={`${activity.color} text-white rounded-3xl p-8
                       transform hover:scale-105 transition-all duration-200
                       shadow-lg hover:shadow-2xl animate-fadeIn group relative overflow-hidden`}
                    >
                        <div className="absolute top-0 right-0 w-32 h-32 bg-white/10 rounded-full -mr-16 -mt-16 transition-transform group-hover:scale-150" />
                        <div className="relative z-10">
                            <div className="text-6xl mb-4 filter drop-shadow-md">{activity.emoji}</div>
                            <h2 className="text-2xl font-black mb-2 tracking-tight">{activity.title}</h2>
                            <p className="text-white/90 font-medium text-lg leading-snug">{activity.description}</p>
                        </div>
                    </Link>
                ))}
            </div>

            {/* Help Card */}
            <div className="max-w-4xl mx-auto mt-8">
                <div className="bg-white rounded-3xl p-8 shadow-sm border border-blue-100 flex items-center gap-6">
                    <div className="text-4xl bg-blue-50 p-4 rounded-2xl">🆘</div>
                    <div>
                        <h3 className="font-bold text-xl text-gray-800 mb-1">Need Help?</h3>
                        <p className="text-gray-600 text-lg">
                            Raise your hand and ask your teacher if you get stuck.
                        </p>
                    </div>
                </div>
            </div>
        </main>
    );
}
