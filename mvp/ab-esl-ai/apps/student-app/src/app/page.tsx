'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';

export default function JoinPage() {
    const router = useRouter();
    const [classCode, setClassCode] = useState('');
    const [nickname, setNickname] = useState('');
    const [l1, setL1] = useState('es');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const languages = [
        { code: 'ar', name: 'Arabic العربية' },
        { code: 'zh', name: 'Chinese 中文' },
        { code: 'es', name: 'Spanish Español' },
        { code: 'fr', name: 'French Français' },
        { code: 'hi', name: 'Hindi हिन्दी' },
        { code: 'ko', name: 'Korean 한국어' },
        { code: 'pa', name: 'Punjabi ਪੰਜਾਬੀ' },
        { code: 'so', name: 'Somali Soomaali' },
        { code: 'tl', name: 'Tagalog' },
        { code: 'uk', name: 'Ukrainian Українська' },
        { code: 'ur', name: 'Urdu اردو' },
        { code: 'vi', name: 'Vietnamese Tiếng Việt' },
    ];

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        try {
            const res = await fetch('/api/auth/join', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    class_code: classCode.toUpperCase(),
                    nickname,
                    l1,
                }),
            });

            const data = await res.json();

            if (!res.ok) {
                throw new Error(data.detail || 'Could not join class');
            }

            // Store session info
            localStorage.setItem('session', JSON.stringify({
                token: data.token,
                sessionId: data.session_id,
                participantId: data.participant_id,
                nickname,
                l1,
            }));

            router.push('/dashboard');
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Something went wrong');
        } finally {
            setLoading(false);
        }
    };

    return (
        <main className="min-h-screen flex items-center justify-center p-4">
            <div className="w-full max-w-md animate-fadeIn">
                {/* Logo/Title */}
                <div className="text-center mb-8">
                    <div className="text-6xl mb-4">📚</div>
                    <h1 className="text-4xl font-black text-blue-600 mb-2 tracking-tight">
                        ESL Learning
                    </h1>
                    <p className="text-gray-500 text-xl font-medium">Join your class</p>
                </div>

                {/* Join Form */}
                <form onSubmit={handleSubmit} className="card p-8 space-y-6">
                    {error && (
                        <div className="bg-red-50 text-red-600 p-4 rounded-2xl text-center font-medium border border-red-100">
                            {error}
                        </div>
                    )}

                    {/* Class Code */}
                    <div>
                        <label className="block text-gray-700 font-bold mb-2 ml-1" htmlFor="classCode">
                            Class Code
                        </label>
                        <input
                            id="classCode"
                            type="text"
                            value={classCode}
                            onChange={(e) => setClassCode(e.target.value.toUpperCase())}
                            placeholder="ABC123"
                            maxLength={6}
                            className="input-field text-3xl text-center tracking-[0.5em] font-mono uppercase placeholder:tracking-normal"
                            required
                        />
                    </div>

                    {/* Nickname */}
                    <div>
                        <label className="block text-gray-700 font-bold mb-2 ml-1" htmlFor="nickname">
                            Your Name
                        </label>
                        <input
                            id="nickname"
                            type="text"
                            value={nickname}
                            onChange={(e) => setNickname(e.target.value)}
                            placeholder="Enter your name"
                            maxLength={20}
                            className="input-field"
                            required
                        />
                    </div>

                    {/* Language Selection */}
                    <div>
                        <label className="block text-gray-700 font-bold mb-2 ml-1" htmlFor="l1">
                            Your Language
                        </label>
                        <select
                            id="l1"
                            value={l1}
                            onChange={(e) => setL1(e.target.value)}
                            className="input-field appearance-none bg-white"
                        >
                            {languages.map((lang) => (
                                <option key={lang.code} value={lang.code}>
                                    {lang.name}
                                </option>
                            ))}
                        </select>
                    </div>

                    {/* Submit Button */}
                    <button
                        type="submit"
                        disabled={loading || !classCode || !nickname}
                        className="w-full btn btn-primary text-xl shadow-blue-200 hover:shadow-blue-300 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        {loading ? (
                            <span className="animate-pulse">Joining...</span>
                        ) : (
                            <>
                                <span>Start Learning</span>
                                <span>🚀</span>
                            </>
                        )}
                    </button>
                </form>
            </div>
        </main>
    );
}
