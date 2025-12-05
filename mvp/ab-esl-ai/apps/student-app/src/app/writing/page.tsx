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

interface WritingFeedback {
    original: string;
    suggestions: Suggestion[];
    l1_explanations: L1Explanation[];
    vocabulary_suggestions: string[];
    sentence_frames: string[];
}

interface Suggestion {
    type: string;
    original: string;
    suggested: string;
    explanation: string;
}

interface L1Explanation {
    error_type: string;
    explanation: string;
    tip: string;
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const sentenceFrames = {
    narrative: [
        "First, _____.",
        "Next, _____.",
        "Then, _____.",
        "Finally, _____.",
        "In the beginning, _____.",
        "After that, _____.",
    ],
    opinion: [
        "I think _____ because _____.",
        "In my opinion, _____.",
        "I believe that _____.",
        "I agree/disagree because _____.",
        "The best part is _____.",
    ],
    descriptive: [
        "It looks like _____.",
        "It feels like _____.",
        "I can see _____.",
        "The _____ is _____.",
        "There is/are _____.",
    ],
    comparison: [
        "_____ is similar to _____ because _____.",
        "_____ is different from _____ because _____.",
        "Both _____ and _____ are _____.",
        "Unlike _____, _____ is _____.",
    ],
};

const vocabularyLadders: Record<string, string[]> = {
    good: ['nice', 'great', 'excellent', 'wonderful', 'amazing', 'fantastic'],
    bad: ['not good', 'poor', 'terrible', 'awful', 'dreadful'],
    big: ['large', 'huge', 'enormous', 'massive', 'gigantic'],
    small: ['little', 'tiny', 'minute', 'microscopic'],
    happy: ['glad', 'pleased', 'delighted', 'thrilled', 'ecstatic'],
    sad: ['unhappy', 'upset', 'miserable', 'heartbroken', 'devastated'],
    said: ['stated', 'explained', 'exclaimed', 'whispered', 'shouted'],
    walk: ['stroll', 'march', 'stride', 'trudge', 'wander'],
};

export default function WritingPage() {
    const router = useRouter();
    const [session, setSession] = useState<SessionData | null>(null);
    const [text, setText] = useState('');
    const [writingType, setWritingType] = useState<keyof typeof sentenceFrames>('narrative');
    const [feedback, setFeedback] = useState<WritingFeedback | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [showFrames, setShowFrames] = useState(true);
    const [selectedWord, setSelectedWord] = useState<string | null>(null);

    useEffect(() => {
        const stored = localStorage.getItem('session');
        if (!stored) {
            router.push('/');
            return;
        }
        setSession(JSON.parse(stored));
    }, [router]);

    const insertFrame = (frame: string) => {
        const newText = text + (text ? ' ' : '') + frame;
        setText(newText);
    };

    const upgradeWord = (original: string, upgrade: string) => {
        const regex = new RegExp(`\\b${original}\\b`, 'gi');
        setText(text.replace(regex, upgrade));
        setSelectedWord(null);
    };

    const checkText = (word: string) => {
        const lowerWord = word.toLowerCase();
        if (vocabularyLadders[lowerWord]) {
            setSelectedWord(lowerWord);
        }
    };

    const getFeedback = async () => {
        if (!text.trim()) {
            setError('Please write something first!');
            return;
        }

        setLoading(true);
        setError('');

        try {
            const response = await fetch(`${API_URL}/v1/writing/feedback`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    text,
                    l1: session?.l1 || 'es',
                    writing_type: writingType,
                }),
            });

            if (response.ok) {
                const data = await response.json();
                setFeedback(data);
            } else {
                // Fallback for demo purposes
                setFeedback(generateLocalFeedback(text, session?.l1 || 'es'));
            }
        } catch (_err) {
            // Fallback for demo
            setFeedback(generateLocalFeedback(text, session?.l1 || 'es'));
        } finally {
            setLoading(false);
        }
    };

    const generateLocalFeedback = (text: string, l1: string): WritingFeedback => {
        const suggestions: Suggestion[] = [];
        const l1Explanations: L1Explanation[] = [];

        // Check for common ESL issues
        // Check for missing articles
        const articlePattern = /\b(is|was|have|has|see|need|want)\s+([a-z]+)\b/gi;
        let match;
        while ((match = articlePattern.exec(text)) !== null) {
            const word = match[2].toLowerCase();
            if (!['a', 'an', 'the', 'my', 'your', 'his', 'her', 'its', 'our', 'their'].includes(word)) {
                suggestions.push({
                    type: 'article',
                    original: match[0],
                    suggested: `${match[1]} a ${word}`,
                    explanation: 'Consider adding an article (a/an/the) before the noun',
                });
            }
        }

        // Check for simple word upgrades
        Object.keys(vocabularyLadders).forEach(word => {
            if (text.toLowerCase().includes(word)) {
                const upgrades = vocabularyLadders[word];
                suggestions.push({
                    type: 'vocabulary',
                    original: word,
                    suggested: upgrades[Math.min(1, upgrades.length - 1)],
                    explanation: `Try using a more specific word: ${upgrades.slice(0, 3).join(', ')}`,
                });
            }
        });

        // L1-specific explanations
        if (['ar', 'zh', 'ko', 'ja'].includes(l1)) {
            l1Explanations.push({
                error_type: 'articles',
                explanation: 'English uses "a/an" for one thing (first time) and "the" for specific things.',
                tip: 'Ask: Is this the first time mentioning it? Use "a/an". Is it specific? Use "the".',
            });
        }

        if (['es', 'pt', 'it', 'fr'].includes(l1)) {
            l1Explanations.push({
                error_type: 'word_order',
                explanation: 'In English, adjectives usually come BEFORE nouns (not after).',
                tip: 'Say "big house" not "house big"',
            });
        }

        return {
            original: text,
            suggestions,
            l1_explanations: l1Explanations,
            vocabulary_suggestions: ['First', 'Next', 'Then', 'Finally', 'However', 'Because'],
            sentence_frames: sentenceFrames[writingType],
        };
    };

    const speakText = (text: string) => {
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = 'en-US';
        utterance.rate = 0.8;
        speechSynthesis.speak(utterance);
    };

    if (!session) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-gray-50">
                <div className="animate-pulse text-2xl text-indigo-600 font-bold">Loading...</div>
            </div>
        );
    }

    return (
        <main className="min-h-screen bg-[radial-gradient(circle_at_center,_var(--tw-gradient-stops))] from-indigo-100 via-white to-indigo-50 p-6 pb-24">
            <div className="max-w-6xl mx-auto">
                {/* Header */}
                <header className="flex items-center justify-between mb-8">
                    <Link
                        href="/dashboard"
                        className="w-12 h-12 flex items-center justify-center bg-white rounded-full shadow-lg text-2xl hover:scale-110 transition-transform"
                        aria-label="Back to Dashboard"
                    >
                        ←
                    </Link>
                    <h1 className="text-3xl font-bold text-gray-800">
                        <span className="mr-2">✏️</span> Writing Helper
                    </h1>
                    <div className="w-12" />
                </header>

                {error && (
                    <div className="bg-red-50 text-red-600 p-4 rounded-2xl mb-6 border border-red-100 shadow-sm">
                        {error}
                    </div>
                )}

                {/* Writing Type Selector */}
                <div className="bg-white/80 backdrop-blur-md rounded-[2rem] shadow-lg p-6 mb-8 border border-white/50">
                    <label className="block text-lg font-bold text-gray-700 mb-4">
                        What are you writing?
                    </label>
                    <div className="flex flex-wrap gap-3">
                        {Object.keys(sentenceFrames).map((type) => (
                            <button
                                key={type}
                                onClick={() => setWritingType(type as keyof typeof sentenceFrames)}
                                className={`px-6 py-3 rounded-xl capitalize font-bold transition-all duration-300 ${writingType === type
                                    ? 'bg-indigo-600 text-white shadow-lg scale-105'
                                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                                    }`}
                            >
                                {type}
                            </button>
                        ))}
                    </div>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                    {/* Writing Area */}
                    <div className="lg:col-span-2 space-y-6">
                        <div className="bg-white/80 backdrop-blur-md rounded-[2.5rem] shadow-xl p-6 border border-white/50">
                            <textarea
                                value={text}
                                onChange={(e) => setText(e.target.value)}
                                onDoubleClick={() => {
                                    const selection = window.getSelection()?.toString().trim();
                                    if (selection) checkText(selection);
                                }}
                                placeholder="Start writing here... Double-click a word to see vocabulary options."
                                className="w-full h-96 p-6 border-2 border-indigo-100 rounded-[2rem]
                                         text-xl leading-relaxed resize-none bg-white/50
                                         focus:border-indigo-500 focus:ring-4 focus:ring-indigo-100 outline-none transition-all"
                            />

                            <div className="flex items-center justify-between mt-6 px-2">
                                <span className="text-sm font-bold text-gray-500 bg-gray-100 px-3 py-1 rounded-full">
                                    {text.split(/\s+/).filter(w => w).length} words
                                </span>
                                <div className="flex gap-3">
                                    <button
                                        onClick={() => speakText(text)}
                                        disabled={!text}
                                        className="px-6 py-3 bg-gray-100 text-gray-700 rounded-xl font-bold hover:bg-gray-200
                                                 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                                    >
                                        🔊 Listen
                                    </button>
                                    <button
                                        onClick={getFeedback}
                                        disabled={loading || !text}
                                        className="px-8 py-3 bg-indigo-600 text-white rounded-xl font-bold shadow-lg
                                                 hover:bg-indigo-700 disabled:opacity-50
                                                 disabled:cursor-not-allowed transition-all hover:scale-105"
                                    >
                                        {loading ? 'Checking...' : '✨ Get Help'}
                                    </button>
                                </div>
                            </div>
                        </div>

                        {/* Feedback Display */}
                        {feedback && (
                            <div className="space-y-6 animate-in slide-in-from-bottom-4 duration-500">
                                {/* Suggestions */}
                                {feedback.suggestions.length > 0 && (
                                    <div className="bg-white/80 backdrop-blur-md rounded-[2.5rem] shadow-xl p-8 border border-white/50">
                                        <h3 className="text-xl font-bold text-gray-800 mb-6 flex items-center gap-2">
                                            <span>💡</span> Suggestions
                                        </h3>
                                        <div className="space-y-4">
                                            {feedback.suggestions.map((sug, idx) => (
                                                <div
                                                    key={idx}
                                                    className="p-6 bg-yellow-50/80 rounded-[2rem] border border-yellow-100"
                                                >
                                                    <div className="flex items-center gap-2 mb-2">
                                                        <span className="text-xs font-bold bg-yellow-200 text-yellow-800 px-2 py-1 rounded-lg uppercase tracking-wide">
                                                            {sug.type}
                                                        </span>
                                                    </div>
                                                    <p className="text-lg mb-2">
                                                        <span className="line-through text-gray-400 decoration-2">
                                                            {sug.original}
                                                        </span>
                                                        <span className="mx-2 text-gray-400">→</span>
                                                        <span className="font-bold text-green-600 bg-green-50 px-2 py-1 rounded-lg">
                                                            {sug.suggested}
                                                        </span>
                                                    </p>
                                                    <p className="text-gray-600 text-sm mb-4">
                                                        {sug.explanation}
                                                    </p>
                                                    <button
                                                        onClick={() => {
                                                            setText(text.replace(sug.original, sug.suggested));
                                                        }}
                                                        className="text-sm px-4 py-2 bg-green-500 text-white rounded-xl font-bold 
                                                                 hover:bg-green-600 transition-colors shadow-sm"
                                                    >
                                                        Apply Fix
                                                    </button>
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                )}

                                {/* L1 Explanations */}
                                {feedback.l1_explanations.length > 0 && (
                                    <div className="bg-white/80 backdrop-blur-md rounded-[2.5rem] shadow-xl p-8 border border-white/50">
                                        <h3 className="text-xl font-bold text-gray-800 mb-6 flex items-center gap-2">
                                            <span>🌍</span> Tips for Your Language
                                        </h3>
                                        <div className="space-y-4">
                                            {feedback.l1_explanations.map((exp, idx) => (
                                                <div
                                                    key={idx}
                                                    className="p-6 bg-blue-50/80 rounded-[2rem] border border-blue-100"
                                                >
                                                    <p className="font-bold text-blue-900 mb-2">
                                                        {exp.explanation}
                                                    </p>
                                                    <p className="text-sm text-blue-700 bg-blue-100/50 p-3 rounded-xl">
                                                        💡 {exp.tip}
                                                    </p>
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                )}
                            </div>
                        )}
                    </div>

                    {/* Sidebar - Helpers */}
                    <div className="space-y-6">
                        {/* Sentence Frames */}
                        <div className="bg-white/80 backdrop-blur-md rounded-[2.5rem] shadow-xl p-6 border border-white/50">
                            <button
                                onClick={() => setShowFrames(!showFrames)}
                                className="w-full flex items-center justify-between font-bold text-gray-800 text-lg mb-4"
                            >
                                <span className="flex items-center gap-2">📝 Sentence Starters</span>
                                <span className="text-gray-400">{showFrames ? '▼' : '▶'}</span>
                            </button>
                            {showFrames && (
                                <div className="space-y-3 animate-in slide-in-from-top-2 duration-300">
                                    {sentenceFrames[writingType].map((frame, idx) => (
                                        <button
                                            key={idx}
                                            onClick={() => insertFrame(frame)}
                                            className="w-full text-left p-4 text-gray-700 bg-gray-50
                                                     rounded-2xl hover:bg-indigo-50 hover:text-indigo-700 
                                                     transition-all border border-gray-100 hover:border-indigo-100 font-medium"
                                        >
                                            {frame}
                                        </button>
                                    ))}
                                </div>
                            )}
                        </div>

                        {/* Vocabulary Upgrade */}
                        {selectedWord && vocabularyLadders[selectedWord] && (
                            <div className="bg-white/80 backdrop-blur-md rounded-[2.5rem] shadow-xl p-6 border border-white/50 animate-in zoom-in duration-300">
                                <h3 className="font-bold text-gray-800 mb-4 flex items-center gap-2">
                                    <span>📚</span> Better words for <span className="text-indigo-600">&quot;{selectedWord}&quot;</span>
                                </h3>
                                <div className="space-y-3">
                                    {vocabularyLadders[selectedWord].map((word, idx) => (
                                        <button
                                            key={idx}
                                            onClick={() => upgradeWord(selectedWord, word)}
                                            className="w-full text-left p-4 bg-green-50 rounded-2xl
                                                     hover:bg-green-100 transition-all flex items-center justify-between
                                                     border border-green-100 group"
                                        >
                                            <span className="font-bold text-green-800 group-hover:text-green-900">{word}</span>
                                            <span className="text-xs font-bold text-green-600 bg-green-200/50 px-2 py-1 rounded-lg">
                                                Level {idx + 1}
                                            </span>
                                        </button>
                                    ))}
                                </div>
                            </div>
                        )}

                        {/* Quick Words */}
                        <div className="bg-white/80 backdrop-blur-md rounded-[2.5rem] shadow-xl p-6 border border-white/50">
                            <h3 className="font-bold text-gray-800 mb-4 flex items-center gap-2">
                                <span>⚡</span> Connecting Words
                            </h3>
                            <div className="flex flex-wrap gap-2">
                                {['First', 'Next', 'Then', 'Finally', 'However', 'Because', 'Also', 'For example'].map((word) => (
                                    <button
                                        key={word}
                                        onClick={() => insertFrame(word + ', ')}
                                        className="px-4 py-2 bg-purple-50 text-purple-700 rounded-xl
                                                 text-sm font-bold hover:bg-purple-100 transition-colors
                                                 border border-purple-100"
                                    >
                                        {word}
                                    </button>
                                ))}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </main>
    );
}
