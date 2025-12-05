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

interface GlossEntry {
    en: string;
    l1: string;
    definition?: string;
}

interface GlossResult {
    translation: string;
    gloss: GlossEntry[];
}

export default function GlossaryPage() {
    const router = useRouter();
    const [session, setSession] = useState<SessionData | null>(null);
    const [inputText, setInputText] = useState('');
    const [result, setResult] = useState<GlossResult | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const languageNames: Record<string, string> = {
        ar: 'Arabic العربية',
        zh: 'Chinese 中文',
        es: 'Spanish Español',
        fr: 'French Français',
        hi: 'Hindi हिन्दी',
        ko: 'Korean 한국어',
        pa: 'Punjabi ਪੰਜਾਬੀ',
        so: 'Somali Soomaali',
        tl: 'Tagalog',
        uk: 'Ukrainian Українська',
        ur: 'Urdu اردو',
        vi: 'Vietnamese Tiếng Việt',
    };

    useEffect(() => {
        const stored = localStorage.getItem('session');
        if (!stored) {
            router.push('/');
            return;
        }
        setSession(JSON.parse(stored));
    }, [router]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!inputText.trim() || !session) return;

        setError('');
        setLoading(true);

        try {
            const res = await fetch('/api/v1/captions/gloss', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    text: inputText,
                    l1: session.l1,
                    top_k: 10,
                }),
            });

            if (!res.ok) {
                throw new Error('Failed to get translation');
            }

            const data = await res.json();
            setResult(data);
        } catch (_err) {
            setError('Could not get translation. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    const speakWord = (word: string, lang: string = 'en-US') => {
        const utterance = new SpeechSynthesisUtterance(word);
        utterance.lang = lang;
        utterance.rate = 0.8;
        speechSynthesis.speak(utterance);
    };

    if (!session) {
        return (
            <div className="min-h-screen flex items-center justify-center">
                <div className="animate-pulse text-2xl">Loading...</div>
            </div>
        );
    }

    return (
        <main className="min-h-screen bg-gray-50 pb-20 relative overflow-hidden">
            {/* Background Pattern */}
            <div className="fixed inset-0 opacity-[0.03] pointer-events-none bg-[radial-gradient(#6366f1_2px,transparent_2px)] bg-[length:24px_24px]" />

            {/* Header */}
            <header className="sticky top-0 z-10 bg-white/80 backdrop-blur-md border-b border-white/20 shadow-sm">
                <div className="max-w-md mx-auto px-4 h-16 flex items-center justify-between">
                    <Link
                        href="/dashboard"
                        className="w-10 h-10 flex items-center justify-center rounded-full bg-gray-100 text-gray-600 hover:bg-gray-200 transition-all active:scale-95"
                    >
                        <span className="text-xl">←</span>
                    </Link>
                    <h1 className="text-xl font-bold text-gray-800">My Language</h1>
                    <div className="w-10" />
                </div>
            </header>

            <div className="max-w-md mx-auto p-4 relative z-0">
                <div className="text-center mb-6 animate-slide-up">
                    <span className="text-6xl mb-4 block">🌍</span>
                    <p className="text-gray-600 font-medium">
                        See English words in <span className="text-indigo-600 font-bold">{languageNames[session.l1] || session.l1}</span>
                    </p>
                </div>

                {/* Input Form */}
                <form onSubmit={handleSubmit} className="mb-8 animate-slide-up">
                    <div className="bg-white rounded-[2rem] shadow-xl p-6 border border-gray-100 relative overflow-hidden group focus-within:ring-4 focus-within:ring-indigo-100 transition-all">
                        <textarea
                            value={inputText}
                            onChange={(e) => setInputText(e.target.value)}
                            placeholder="Type or paste English text here..."
                            className="w-full text-xl border-0 focus:ring-0 resize-none h-40
                       placeholder-gray-300 bg-transparent font-medium text-gray-800"
                        />
                        <div className="absolute bottom-4 right-4">
                            <button
                                type="submit"
                                disabled={loading || !inputText.trim()}
                                className="bg-indigo-600 hover:bg-indigo-700 text-white
                     font-bold py-3 px-6 rounded-xl transition-all active:scale-95
                     disabled:opacity-50 disabled:cursor-not-allowed disabled:active:scale-100
                     flex items-center justify-center gap-2 shadow-lg shadow-indigo-200"
                            >
                                {loading ? (
                                    <>
                                        <span className="animate-spin">⏳</span>
                                        Translating...
                                    </>
                                ) : (
                                    <>
                                        <span>🔍</span> Find Words
                                    </>
                                )}
                            </button>
                        </div>
                    </div>
                </form>

                {error && (
                    <div className="bg-red-50 border border-red-100 text-red-600 p-4 rounded-2xl mb-6 flex items-center gap-3 animate-slide-up">
                        <span className="text-2xl">⚠️</span>
                        <p className="font-medium">{error}</p>
                    </div>
                )}

                {/* Results */}
                {result && (
                    <div className="animate-slide-up space-y-6">
                        {/* Translation */}
                        <div className="bg-white rounded-[2rem] shadow-lg p-6 border border-gray-100">
                            <h2 className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-4">Translation</h2>
                            <p className="text-2xl font-medium text-gray-800 leading-relaxed">{result.translation}</p>
                        </div>

                        {/* Vocabulary List */}
                        {result.gloss.length > 0 && (
                            <div className="bg-white rounded-[2rem] shadow-lg p-6 border border-gray-100">
                                <h2 className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-4">Key Words</h2>
                                <div className="space-y-4">
                                    {result.gloss.map((entry, i) => (
                                        <div
                                            key={i}
                                            className="flex items-center justify-between p-4
                             bg-gray-50 rounded-2xl border border-gray-100 hover:bg-indigo-50 hover:border-indigo-100 transition-colors group"
                                        >
                                            <div className="flex-1">
                                                <div className="flex items-center gap-3 mb-1">
                                                    <span className="text-xl font-bold text-indigo-600">
                                                        {entry.en}
                                                    </span>
                                                    <button
                                                        onClick={() => speakWord(entry.en)}
                                                        className="w-8 h-8 bg-white rounded-full flex items-center justify-center text-gray-400 hover:text-indigo-600 shadow-sm transition-colors active:scale-95"
                                                        aria-label={`Listen to ${entry.en}`}
                                                    >
                                                        🔊
                                                    </button>
                                                </div>
                                                <div className="text-2xl font-medium text-gray-800">{entry.l1}</div>
                                                {entry.definition && (
                                                    <div className="text-sm text-gray-500 mt-2 bg-white p-2 rounded-lg inline-block border border-gray-100">
                                                        {entry.definition}
                                                    </div>
                                                )}
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}

                        {/* Try Again */}
                        <button
                            onClick={() => {
                                setResult(null);
                                setInputText('');
                            }}
                            className="w-full bg-white hover:bg-gray-50 text-gray-700 border-2 border-gray-100
                     font-bold py-4 rounded-2xl transition-all active:scale-95 text-lg shadow-sm"
                        >
                            ✨ Try Different Text
                        </button>
                    </div>
                )}

                {/* Helpful hint when empty */}
                {!result && !loading && (
                    <div className="text-center text-gray-500 mt-8 animate-slide-up delay-100">
                        <p className="text-lg font-bold mb-4 text-gray-400">💡 Try typing:</p>
                        <div className="flex flex-wrap gap-3 justify-center">
                            {['open your book', 'sit down please', 'good morning class'].map((example) => (
                                <button
                                    key={example}
                                    onClick={() => setInputText(example)}
                                    className="bg-white hover:bg-indigo-50 border border-gray-200 hover:border-indigo-200 px-5 py-3 rounded-full
                         text-gray-600 hover:text-indigo-600 font-medium transition-all active:scale-95 shadow-sm"
                                >
                                    {example}
                                </button>
                            ))}
                        </div>
                    </div>
                )}
            </div>
        </main>
    );
}
