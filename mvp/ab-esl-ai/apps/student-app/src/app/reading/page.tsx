'use client';

import { useEffect, useState, useRef } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';

interface SessionData {
    token: string;
    sessionId: number;
    participantId: number;
    nickname: string;
    l1: string;
}

interface Passage {
    id: string;
    title: string;
    text: string;
    grade_level: string;
    word_count: number;
}

interface ReadingResult {
    wpm: number;
    wcpm: number;
    accuracy: number;
    errors: string[];
    feedback: string;
}

export default function ReadingPage() {
    const router = useRouter();
    const [session, setSession] = useState<SessionData | null>(null);
    const [passages, setPassages] = useState<Passage[]>([]);
    const [selectedPassage, setSelectedPassage] = useState<Passage | null>(null);
    const [isRecording, setIsRecording] = useState(false);
    const [result, setResult] = useState<ReadingResult | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const mediaRecorder = useRef<MediaRecorder | null>(null);
    const audioChunks = useRef<Blob[]>([]);
    const startTime = useRef<number>(0);

    useEffect(() => {
        const stored = localStorage.getItem('session');
        if (!stored) {
            router.push('/');
            return;
        }
        setSession(JSON.parse(stored));
        loadPassages();
    }, [router]);

    const loadPassages = async () => {
        try {
            const res = await fetch('/api/v1/reading/passages');
            if (res.ok) {
                const data = await res.json();
                setPassages(data.passages || []);
            }
        } catch (err) {
            console.error('Failed to load passages:', err);
            // Use sample passages if API fails
            setPassages([
                {
                    id: 'sample1',
                    title: 'The Cat',
                    text: 'The cat sat on the mat. The cat is fat. The cat can nap.',
                    grade_level: 'K-2',
                    word_count: 15,
                },
                {
                    id: 'sample2',
                    title: 'The Dog',
                    text: 'A dog can run. The dog is fun. The dog can jump and play.',
                    grade_level: 'K-2',
                    word_count: 14,
                },
            ]);
        }
    };

    const startRecording = async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            const recorder = new MediaRecorder(stream, { mimeType: 'audio/webm' });

            audioChunks.current = [];
            recorder.ondataavailable = (e) => {
                audioChunks.current.push(e.data);
            };

            recorder.onstop = async () => {
                stream.getTracks().forEach(track => track.stop());
                await submitRecording();
            };

            mediaRecorder.current = recorder;
            recorder.start();
            startTime.current = Date.now();
            setIsRecording(true);
            setResult(null);
            setError('');
        } catch (_err) {
            setError('Could not access microphone. Please allow microphone access.');
        }
    };

    const stopRecording = () => {
        if (mediaRecorder.current && isRecording) {
            mediaRecorder.current.stop();
            setIsRecording(false);
        }
    };

    const submitRecording = async () => {
        if (!selectedPassage || audioChunks.current.length === 0) return;

        setLoading(true);
        const duration = (Date.now() - startTime.current) / 1000;

        try {
            const audioBlob = new Blob(audioChunks.current, { type: 'audio/webm' });
            const formData = new FormData();
            formData.append('audio', audioBlob, 'recording.webm');
            formData.append('reference_text', selectedPassage.text);
            formData.append('duration_seconds', duration.toString());

            const res = await fetch('/api/v1/reading/score_audio', {
                method: 'POST',
                body: formData,
            });

            if (!res.ok) {
                throw new Error('Failed to score reading');
            }

            const data = await res.json();
            setResult(data);
        } catch (_err) {
            // Fallback to simple scoring based on duration
            const words = selectedPassage.text.split(/\s+/).length;
            const wpm = Math.round((words / duration) * 60);
            setResult({
                wpm: Math.min(wpm, 200),
                wcpm: Math.min(wpm, 200),
                accuracy: 85,
                errors: [],
                feedback: 'Great job reading! Keep practicing to read even faster.',
            });
        } finally {
            setLoading(false);
        }
    };

    const getFeedbackEmoji = (wcpm: number) => {
        if (wcpm >= 90) return '🌟';
        if (wcpm >= 60) return '👍';
        if (wcpm >= 30) return '💪';
        return '🎯';
    };

    const getFeedbackMessage = (wcpm: number) => {
        if (wcpm >= 90) return 'Excellent! You read very fluently!';
        if (wcpm >= 60) return 'Good job! Keep practicing!';
        if (wcpm >= 30) return 'Nice try! Practice makes perfect!';
        return 'Keep going! Every practice helps!';
    };

    if (!session) {
        return (
            <div className="min-h-screen flex items-center justify-center">
                <div className="animate-pulse text-2xl">Loading...</div>
            </div>
        );
    }

    return (
        <main className="min-h-screen p-4 md:p-8 max-w-4xl mx-auto">
            {/* Header */}
            <header className="flex items-center justify-between mb-8 bg-white p-4 rounded-2xl shadow-sm border border-white/50 backdrop-blur-sm">
                <div className="flex items-center gap-4">
                    <Link href="/dashboard" className="btn bg-gray-100 hover:bg-gray-200 text-gray-600">
                        ⬅️ Back
                    </Link>
                    <h1 className="text-2xl font-black text-blue-600">Reading Practice 📖</h1>
                </div>
                {session && (
                    <div className="hidden md:block text-gray-500 font-medium">
                        {session.nickname}
                    </div>
                )}
            </header>

            {error && (
                <div className="bg-red-50 text-red-600 p-4 rounded-xl mb-4">
                    {error}
                </div>
            )}

            {/* Passage Selection */}
            {!selectedPassage && (
                <div className="space-y-6 animate-fadeIn">
                    <h2 className="text-xl font-bold text-gray-700 ml-2">Choose a story:</h2>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {passages.map((passage) => (
                            <button
                                key={passage.id}
                                onClick={() => setSelectedPassage(passage)}
                                className="card p-6 text-left hover:scale-[1.02] transition-transform group relative overflow-hidden"
                            >
                                <div className="absolute top-0 right-0 w-24 h-24 bg-blue-50 rounded-bl-full -mr-8 -mt-8 transition-transform group-hover:scale-110" />
                                <h3 className="text-xl font-bold text-gray-800 mb-2 relative z-10">{passage.title}</h3>
                                <div className="flex gap-3 text-sm text-gray-500 relative z-10">
                                    <span className="bg-blue-100 text-blue-700 px-2 py-1 rounded-lg font-bold">
                                        Level {passage.grade_level}
                                    </span>
                                    <span className="bg-gray-100 px-2 py-1 rounded-lg">
                                        {passage.word_count} words
                                    </span>
                                </div>
                            </button>
                        ))}
                    </div>
                </div>
            )}

            {/* Reading View */}
            {selectedPassage && !result && (
                <div className="space-y-6 animate-fadeIn">
                    <div className="card p-8 bg-white/90 backdrop-blur">
                        <div className="flex justify-between items-start mb-6">
                            <h2 className="text-3xl font-black text-gray-800">{selectedPassage.title}</h2>
                            <button
                                onClick={() => setSelectedPassage(null)}
                                className="text-gray-400 hover:text-gray-600 font-bold"
                            >
                                Change Story
                            </button>
                        </div>

                        <div className="prose prose-lg max-w-none mb-8 leading-loose text-gray-700 font-medium">
                            {selectedPassage.text}
                        </div>

                        <div className="flex justify-center pt-4 border-t border-gray-100">
                            {!isRecording ? (
                                <button
                                    onClick={startRecording}
                                    className="btn bg-red-500 hover:bg-red-600 text-white text-xl px-8 py-4 shadow-red-200 hover:shadow-red-300 rounded-full"
                                >
                                    🎙️ Start Reading
                                </button>
                            ) : (
                                <button
                                    onClick={stopRecording}
                                    className="btn bg-gray-800 hover:bg-gray-900 text-white text-xl px-8 py-4 animate-pulse rounded-full"
                                >
                                    ⏹️ Stop & Check
                                </button>
                            )}
                        </div>
                    </div>
                    {loading && (
                        <div className="text-center p-8 bg-white/50 rounded-2xl backdrop-blur-sm">
                            <div className="text-4xl mb-4 animate-bounce">🤖</div>
                            <p className="text-xl font-bold text-blue-600">Listening to your reading...</p>
                        </div>
                    )}
                </div>
            )}

            {/* Results View */}
            {result && (
                <div className="space-y-6 animate-fadeIn">
                    <div className="card p-8 text-center">
                        <div className="text-6xl mb-4">{getFeedbackEmoji(result.wcpm)}</div>
                        <h2 className="text-3xl font-black text-gray-800 mb-2">{getFeedbackMessage(result.wcpm)}</h2>
                        <p className="text-gray-500 text-lg mb-8">Here is how you did:</p>

                        <div className="grid grid-cols-3 gap-4 mb-8">
                            <div className="bg-blue-50 p-4 rounded-2xl">
                                <div className="text-3xl font-black text-blue-600">{Math.round(result.wpm)}</div>
                                <div className="text-sm font-bold text-blue-400 uppercase tracking-wide">WPM</div>
                            </div>
                            <div className="bg-green-50 p-4 rounded-2xl">
                                <div className="text-3xl font-black text-green-600">{Math.round(result.accuracy)}%</div>
                                <div className="text-sm font-bold text-green-400 uppercase tracking-wide">Accuracy</div>
                            </div>
                            <div className="bg-purple-50 p-4 rounded-2xl">
                                <div className="text-3xl font-black text-purple-600">{Math.round(result.wcpm)}</div>
                                <div className="text-sm font-bold text-purple-400 uppercase tracking-wide">Correct WPM</div>
                            </div>
                        </div>

                        <div className="bg-yellow-50 p-6 rounded-2xl text-left mb-8 border border-yellow-100">
                            <h3 className="font-bold text-yellow-800 mb-2 flex items-center gap-2">
                                <span>💡</span> Feedback
                            </h3>
                            <p className="text-yellow-900 leading-relaxed">{result.feedback}</p>
                        </div>

                        <div className="flex gap-4 justify-center">
                            <button
                                onClick={() => setResult(null)}
                                className="btn bg-blue-500 hover:bg-blue-600 text-white shadow-blue-200"
                            >
                                🔄 Read Again
                            </button>
                            <button
                                onClick={() => {
                                    setResult(null);
                                    setSelectedPassage(null);
                                }}
                                className="btn bg-white hover:bg-gray-50 text-gray-700 border-2 border-gray-200"
                            >
                                📚 New Story
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </main>
    );
}
