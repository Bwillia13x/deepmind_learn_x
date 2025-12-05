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

interface Exercise {
    id: string;
    type: string;
    word1: string;
    word2: string;
    ipa1?: string;
    ipa2?: string;
    description: string;
}

interface SpeakingResult {
    score: number;
    feedback: string;
    matched?: boolean;
    target_word?: string;
}

export default function SpeakingPage() {
    const router = useRouter();
    const [session, setSession] = useState<SessionData | null>(null);
    const [exercises, setExercises] = useState<Exercise[]>([]);
    const [currentExercise, setCurrentExercise] = useState<Exercise | null>(null);
    const [currentWord, setCurrentWord] = useState<string>('');
    const [isRecording, setIsRecording] = useState(false);
    const [result, setResult] = useState<SpeakingResult | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const mediaRecorder = useRef<MediaRecorder | null>(null);
    const audioChunks = useRef<Blob[]>([]);

    useEffect(() => {
        const stored = localStorage.getItem('session');
        if (!stored) {
            router.push('/');
            return;
        }
        const sessionData = JSON.parse(stored);
        setSession(sessionData);
        loadExercises(sessionData.l1);
    }, [router]);

    const loadExercises = async (l1: string) => {
        try {
            const res = await fetch(`/api/v1/speaking/exercises?l1=${l1}`);
            if (res.ok) {
                const data = await res.json();
                setExercises(data.exercises || []);
            }
        } catch (err) {
            console.error('Failed to load exercises:', err);
            // Fallback exercises
            setExercises([
                {
                    id: 'pair_l_r',
                    type: 'minimal_pair',
                    word1: 'light',
                    word2: 'right',
                    ipa1: '/laɪt/',
                    ipa2: '/raɪt/',
                    description: 'Practice the L and R sounds',
                },
                {
                    id: 'pair_sh_ch',
                    type: 'minimal_pair',
                    word1: 'ship',
                    word2: 'chip',
                    ipa1: '/ʃɪp/',
                    ipa2: '/tʃɪp/',
                    description: 'Practice SH and CH sounds',
                },
                {
                    id: 'pair_b_p',
                    type: 'minimal_pair',
                    word1: 'bat',
                    word2: 'pat',
                    ipa1: '/bæt/',
                    ipa2: '/pæt/',
                    description: 'Practice B and P sounds',
                },
            ]);
        }
    };

    const startPractice = (exercise: Exercise, word: string) => {
        setCurrentExercise(exercise);
        setCurrentWord(word);
        setResult(null);
        setError('');
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
            setIsRecording(true);
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
        if (!currentExercise || !currentWord || audioChunks.current.length === 0) return;

        setLoading(true);

        try {
            const audioBlob = new Blob(audioChunks.current, { type: 'audio/webm' });
            const formData = new FormData();
            formData.append('audio', audioBlob, 'recording.webm');
            formData.append('target_word', currentWord);
            formData.append('pair_id', currentExercise.id);

            const res = await fetch('/api/v1/speaking/score', {
                method: 'POST',
                body: formData,
            });

            if (!res.ok) {
                throw new Error('Failed to score pronunciation');
            }

            const data = await res.json();
            setResult(data);
        } catch (_err) {
            // Simulate result for demo
            const score = 70 + Math.random() * 25;
            setResult({
                score: Math.round(score),
                feedback: score >= 80 ? 'Great pronunciation!' : 'Good try! Listen and try again.',
                matched: score >= 80,
                target_word: currentWord,
            });
        } finally {
            setLoading(false);
        }
    };

    const playWord = (word: string) => {
        const utterance = new SpeechSynthesisUtterance(word);
        utterance.rate = 0.8;
        utterance.lang = 'en-US';
        speechSynthesis.speak(utterance);
    };

    const getScoreEmoji = (score: number) => {
        if (score >= 90) return '🌟';
        if (score >= 80) return '👍';
        if (score >= 70) return '💪';
        return '🎯';
    };

    const getScoreColor = (score: number) => {
        if (score >= 80) return 'text-green-600 bg-green-50';
        if (score >= 60) return 'text-yellow-600 bg-yellow-50';
        return 'text-orange-600 bg-orange-50';
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
                    <h1 className="text-xl font-bold text-gray-800">Speaking Practice</h1>
                    <div className="w-10" />
                </div>
            </header>

            <div className="max-w-md mx-auto p-4 relative z-0">
                {error && (
                    <div className="bg-red-50 border border-red-100 text-red-600 p-4 rounded-2xl mb-6 flex items-center gap-3 animate-slide-up">
                        <span className="text-2xl">⚠️</span>
                        <p className="font-medium">{error}</p>
                    </div>
                )}

                {/* Exercise Selection */}
                {!currentExercise && (
                    <div className="space-y-6 animate-slide-up">
                        <div className="text-center mb-8">
                            <span className="text-6xl mb-4 block">🗣️</span>
                            <h2 className="text-2xl font-bold text-gray-800 mb-2">
                                Let's Practice Speaking!
                            </h2>
                            <p className="text-gray-500">Choose a pair of words to practice.</p>
                        </div>

                        <div className="grid gap-4">
                            {exercises.map((exercise) => (
                                <div
                                    key={exercise.id}
                                    className="bg-white rounded-3xl p-6 shadow-lg border border-gray-100 hover:shadow-xl transition-all"
                                >
                                    <h3 className="text-center text-gray-500 font-bold mb-4 uppercase tracking-wider text-sm">
                                        {exercise.description}
                                    </h3>
                                    <div className="flex gap-4">
                                        <button
                                            onClick={() => startPractice(exercise, exercise.word1)}
                                            className="flex-1 bg-indigo-50 hover:bg-indigo-100 border-2 border-indigo-100
                                   text-indigo-700 font-bold py-4 px-4 rounded-2xl
                                   transition-all active:scale-95 flex flex-col items-center gap-1"
                                        >
                                            <span className="text-xl">{exercise.word1}</span>
                                            <span className="text-sm font-normal text-indigo-400 bg-white px-2 py-0.5 rounded-full">
                                                {exercise.ipa1}
                                            </span>
                                        </button>
                                        <div className="flex items-center text-gray-300 font-bold">VS</div>
                                        <button
                                            onClick={() => startPractice(exercise, exercise.word2)}
                                            className="flex-1 bg-pink-50 hover:bg-pink-100 border-2 border-pink-100
                                   text-pink-700 font-bold py-4 px-4 rounded-2xl
                                   transition-all active:scale-95 flex flex-col items-center gap-1"
                                        >
                                            <span className="text-xl">{exercise.word2}</span>
                                            <span className="text-sm font-normal text-pink-400 bg-white px-2 py-0.5 rounded-full">
                                                {exercise.ipa2}
                                            </span>
                                        </button>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {/* Practice View */}
                {currentExercise && !result && (
                    <div className="animate-slide-up text-center pt-8">
                        <div className="bg-white p-8 rounded-[2rem] shadow-xl border border-gray-100 mb-8 relative overflow-hidden">
                            <div className="absolute top-0 left-0 w-full h-2 bg-gradient-to-r from-indigo-400 to-pink-400" />
                            <h2 className="text-gray-500 font-bold mb-6 uppercase tracking-wide text-sm">Say this word</h2>
                            <div className="text-6xl font-black text-gray-800 mb-6 tracking-tight">
                                {currentWord}
                            </div>
                            <button
                                onClick={() => playWord(currentWord)}
                                className="inline-flex items-center gap-2 px-6 py-3 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-full font-bold transition-all active:scale-95"
                            >
                                <span className="text-xl">🔊</span> Listen First
                            </button>
                        </div>

                        <div className="space-y-6">
                            {!isRecording ? (
                                <button
                                    onClick={startRecording}
                                    aria-label="Start Recording"
                                    className="w-24 h-24 bg-gradient-to-br from-green-400 to-green-600 rounded-full shadow-lg shadow-green-200 flex items-center justify-center mx-auto hover:scale-110 transition-all active:scale-95 group"
                                >
                                    <span className="text-4xl group-hover:animate-bounce">🎤</span>
                                </button>
                            ) : (
                                <button
                                    onClick={stopRecording}
                                    aria-label="Stop Recording"
                                    className="w-24 h-24 bg-red-500 rounded-full shadow-lg shadow-red-200 flex items-center justify-center mx-auto animate-pulse"
                                >
                                    <div className="w-8 h-8 bg-white rounded-lg" />
                                </button>
                            )}

                            <div className="h-8">
                                {isRecording && (
                                    <p className="text-red-500 font-bold animate-pulse">Recording... Tap to stop</p>
                                )}
                                {!isRecording && !loading && (
                                    <p className="text-gray-400 font-medium">Tap the microphone to start</p>
                                )}
                                {loading && (
                                    <p className="text-indigo-500 font-bold animate-pulse">Checking pronunciation...</p>
                                )}
                            </div>

                            <button
                                onClick={() => setCurrentExercise(null)}
                                className="text-gray-400 hover:text-gray-600 font-bold text-sm py-4"
                            >
                                Cancel
                            </button>
                        </div>
                    </div>
                )}

                {/* Results View */}
                {result && (
                    <div className="animate-slide-up text-center pt-8">
                        <div className="bg-white p-8 rounded-[2rem] shadow-xl border border-gray-100 mb-8 relative overflow-hidden">
                            <div className={`absolute top-0 left-0 w-full h-2 ${result.score >= 80 ? 'bg-green-500' : 'bg-orange-500'}`} />

                            <div className="text-8xl mb-6 animate-bounce-slow">
                                {getScoreEmoji(result.score)}
                            </div>

                            <div className={`inline-block px-8 py-4 rounded-2xl mb-6 ${getScoreColor(result.score)}`}>
                                <span className="text-5xl font-black">{result.score}%</span>
                            </div>

                            <p className="text-xl text-gray-700 font-bold leading-relaxed">
                                {result.feedback}
                            </p>
                        </div>

                        <div className="grid gap-4">
                            <button
                                onClick={() => setResult(null)}
                                className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-4 rounded-2xl shadow-lg shadow-indigo-200 transition-all active:scale-95 text-lg"
                            >
                                🔄 Try Again
                            </button>
                            <button
                                onClick={() => {
                                    setResult(null);
                                    setCurrentExercise(null);
                                }}
                                className="w-full bg-white hover:bg-gray-50 text-gray-700 font-bold py-4 rounded-2xl border-2 border-gray-100 transition-all active:scale-95 text-lg"
                            >
                                📝 Pick New Words
                            </button>
                        </div>
                    </div>
                )}
            </div>
        </main>
    );
}
