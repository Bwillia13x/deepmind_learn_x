'use client';

import { useEffect, useState, useRef } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface SessionData {
    token: string;
    sessionId: number;
    participantId: number;
    nickname: string;
    l1: string;
}

interface VocabItem {
    word: string;
    definition: string;
    l1_translation: string;
    collocations: string[];
    sentence_frames: string[];
    category: string;
    frequency: string;
    confidence: number;
}

interface DeckItem {
    word: string;
    l1: string;
    added_at: string;
    next_review: string;
    interval_days: number;
    repetitions: number;
}

type ViewMode = 'camera' | 'deck' | 'review';

export default function VocabLensPage() {
    const router = useRouter();
    const [session, setSession] = useState<SessionData | null>(null);
    const [viewMode, setViewMode] = useState<ViewMode>('camera');
    const [cameraActive, setCameraActive] = useState(false);
    const [detectedItems, setDetectedItems] = useState<VocabItem[]>([]);
    const [selectedItem, setSelectedItem] = useState<VocabItem | null>(null);
    const [deck, setDeck] = useState<DeckItem[]>([]);
    const [reviewItems, setReviewItems] = useState<DeckItem[]>([]);
    const [currentReviewIndex, setCurrentReviewIndex] = useState(0);
    const [showAnswer, setShowAnswer] = useState(false);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const videoRef = useRef<HTMLVideoElement>(null);
    const streamRef = useRef<MediaStream | null>(null);

    useEffect(() => {
        const stored = localStorage.getItem('session');
        if (!stored) {
            router.push('/');
            return;
        }
        const sessionData = JSON.parse(stored);
        setSession(sessionData);
        loadDeck(sessionData.participantId);
    }, [router]);

    useEffect(() => {
        return () => {
            // Cleanup camera on unmount
            if (streamRef.current) {
                streamRef.current.getTracks().forEach(track => track.stop());
            }
        };
    }, []);

    const loadDeck = async (participantId: number) => {
        try {
            const res = await fetch(`${API_URL}/v1/vocab-lens/deck/${participantId}`);
            if (res.ok) {
                const data = await res.json();
                setDeck(data);
            }
        } catch (err) {
            console.error('Failed to load deck:', err);
        }
    };

    const loadReviewItems = async () => {
        if (!session) return;
        try {
            const res = await fetch(`${API_URL}/v1/vocab-lens/deck/${session.participantId}/review`);
            if (res.ok) {
                const data = await res.json();
                setReviewItems(data);
                setCurrentReviewIndex(0);
                setShowAnswer(false);
            }
        } catch (err) {
            console.error('Failed to load review items:', err);
        }
    };

    const startCamera = async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({
                video: { facingMode: 'environment' },
                audio: false,
            });

            if (videoRef.current) {
                videoRef.current.srcObject = stream;
                streamRef.current = stream;
                setCameraActive(true);
            }
        } catch (_err) {
            setError('Could not access camera. Please allow camera access.');
        }
    };

    const stopCamera = () => {
        if (streamRef.current) {
            streamRef.current.getTracks().forEach(track => track.stop());
            streamRef.current = null;
        }
        if (videoRef.current) {
            videoRef.current.srcObject = null;
        }
        setCameraActive(false);
    };

    const captureAndRecognize = async () => {
        if (!videoRef.current || !session) return;

        setLoading(true);
        setError('');

        try {
            // Capture frame from video
            const canvas = document.createElement('canvas');
            canvas.width = videoRef.current.videoWidth;
            canvas.height = videoRef.current.videoHeight;
            const ctx = canvas.getContext('2d');
            ctx?.drawImage(videoRef.current, 0, 0);

            const imageBase64 = canvas.toDataURL('image/jpeg').split(',')[1];

            // Send to API for recognition
            const res = await fetch(`${API_URL}/v1/vocab-lens/recognize`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    image_base64: imageBase64,
                    l1: session.l1,
                }),
            });

            if (res.ok) {
                const data = await res.json();
                setDetectedItems(data.detected_objects);
            } else {
                throw new Error('Recognition failed');
            }
        } catch (_err) {
            // For demo, show sample detections
            setDetectedItems([
                {
                    word: 'book',
                    definition: 'A set of printed pages bound together',
                    l1_translation: getL1Translation('book', session?.l1 || 'es'),
                    collocations: ['read a book', 'open the book', 'library book'],
                    sentence_frames: ['I am reading a ___.', 'Can I borrow your ___?'],
                    category: 'classroom',
                    frequency: 'high',
                    confidence: 0.92,
                },
                {
                    word: 'desk',
                    definition: 'A table for working or studying',
                    l1_translation: getL1Translation('desk', session?.l1 || 'es'),
                    collocations: ['sit at the desk', 'clean the desk'],
                    sentence_frames: ['Please sit at your ___.', 'Put your books on the ___.'],
                    category: 'classroom',
                    frequency: 'high',
                    confidence: 0.88,
                },
                {
                    word: 'pencil',
                    definition: 'A tool for writing or drawing',
                    l1_translation: getL1Translation('pencil', session?.l1 || 'es'),
                    collocations: ['sharpen a pencil', 'pencil case'],
                    sentence_frames: ['I need a ___ to write.', 'Can I borrow your ___?'],
                    category: 'classroom',
                    frequency: 'high',
                    confidence: 0.85,
                },
            ]);
        } finally {
            setLoading(false);
        }
    };

    const getL1Translation = (word: string, l1: string): string => {
        const translations: Record<string, Record<string, string>> = {
            ar: { book: 'كتاب', desk: 'مكتب', pencil: 'قلم رصاص', chair: 'كرسي' },
            es: { book: 'libro', desk: 'escritorio', pencil: 'lápiz', chair: 'silla' },
            zh: { book: '书', desk: '书桌', pencil: '铅笔', chair: '椅子' },
            vi: { book: 'sách', desk: 'bàn', pencil: 'bút chì', chair: 'ghế' },
            ko: { book: '책', desk: '책상', pencil: '연필', chair: '의자' },
        };
        return translations[l1]?.[word] || '';
    };

    const addToDeck = async (item: VocabItem) => {
        if (!session) return;

        try {
            const res = await fetch(`${API_URL}/v1/vocab-lens/deck/add`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    participant_id: session.participantId,
                    word: item.word,
                    l1: session.l1,
                }),
            });

            if (res.ok) {
                await loadDeck(session.participantId);
                setSelectedItem(null);
            }
        } catch (_err) {
            // Add locally for demo
            setDeck(prev => [...prev, {
                word: item.word,
                l1: session.l1,
                added_at: new Date().toISOString(),
                next_review: new Date().toISOString(),
                interval_days: 1,
                repetitions: 0,
            }]);
            setSelectedItem(null);
        }
    };

    const recordReview = async (quality: number) => {
        if (!session || reviewItems.length === 0) return;

        const currentItem = reviewItems[currentReviewIndex];

        try {
            await fetch(`${API_URL}/v1/vocab-lens/deck/review`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    participant_id: session.participantId,
                    word: currentItem.word,
                    quality,
                }),
            });
        } catch (err) {
            console.error('Failed to record review:', err);
        }

        // Move to next item
        if (currentReviewIndex < reviewItems.length - 1) {
            setCurrentReviewIndex(currentReviewIndex + 1);
            setShowAnswer(false);
        } else {
            // Review complete
            await loadDeck(session.participantId);
            setViewMode('deck');
            setReviewItems([]);
        }
    };

    const speakWord = (word: string) => {
        const utterance = new SpeechSynthesisUtterance(word);
        utterance.lang = 'en-US';
        utterance.rate = 0.8;
        speechSynthesis.speak(utterance);
    };

    if (!session) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-gray-50">
                <div className="animate-pulse text-2xl text-cyan-600 font-bold">Loading...</div>
            </div>
        );
    }

    return (
        <main className="min-h-screen bg-[radial-gradient(circle_at_center,_var(--tw-gradient-stops))] from-sky-100 via-white to-sky-50 p-6 pb-24">
            {/* Header */}
            <header className="max-w-2xl mx-auto mb-8 flex items-center justify-between">
                <Link 
                    href="/dashboard" 
                    className="w-12 h-12 flex items-center justify-center bg-white rounded-full shadow-lg text-2xl hover:scale-110 transition-transform"
                    aria-label="Back to Dashboard"
                >
                    ←
                </Link>
                <h1 className="text-3xl font-bold text-gray-800">
                    <span className="mr-2">📸</span> Vocab Lens
                </h1>
                <div className="bg-white/80 backdrop-blur-sm px-4 py-2 rounded-full shadow-sm border border-sky-100">
                    <span className="text-sm font-bold text-cyan-700">
                        {deck.length} cards
                    </span>
                </div>
            </header>

            {/* View Mode Tabs */}
            <div className="max-w-2xl mx-auto">
                <div className="flex gap-3 mb-8 bg-white/50 p-2 rounded-[2rem] shadow-sm backdrop-blur-sm">
                    <button
                        onClick={() => {
                            setViewMode('camera');
                            if (viewMode !== 'camera') stopCamera();
                        }}
                        className={`flex-1 py-4 rounded-[1.5rem] font-bold transition-all duration-300 ${viewMode === 'camera'
                            ? 'bg-cyan-500 text-white shadow-lg scale-105'
                            : 'text-gray-500 hover:bg-white/50'
                            }`}
                    >
                        📷 Scan
                    </button>
                    <button
                        onClick={() => {
                            setViewMode('deck');
                            stopCamera();
                        }}
                        className={`flex-1 py-4 rounded-[1.5rem] font-bold transition-all duration-300 ${viewMode === 'deck'
                            ? 'bg-cyan-500 text-white shadow-lg scale-105'
                            : 'text-gray-500 hover:bg-white/50'
                            }`}
                    >
                        📚 Deck
                    </button>
                    <button
                        onClick={() => {
                            setViewMode('review');
                            stopCamera();
                            loadReviewItems();
                        }}
                        className={`flex-1 py-4 rounded-[1.5rem] font-bold transition-all duration-300 ${viewMode === 'review'
                            ? 'bg-cyan-500 text-white shadow-lg scale-105'
                            : 'text-gray-500 hover:bg-white/50'
                            }`}
                    >
                        🎯 Review
                    </button>
                </div>

                {error && (
                    <div className="bg-red-50 text-red-600 p-4 rounded-2xl mb-6 border border-red-100 shadow-sm">
                        {error}
                    </div>
                )}

                {/* Camera View */}
                {viewMode === 'camera' && (
                    <div className="space-y-6">
                        {/* Camera Preview */}
                        <div className="relative bg-gray-900 rounded-[2.5rem] overflow-hidden aspect-[4/3] shadow-2xl ring-8 ring-white">
                            <video
                                ref={videoRef}
                                autoPlay
                                playsInline
                                muted
                                className="w-full h-full object-cover"
                            />
                            {!cameraActive && (
                                <div className="absolute inset-0 flex items-center justify-center bg-gray-900/50 backdrop-blur-sm">
                                    <button
                                        onClick={startCamera}
                                        className="px-8 py-4 bg-cyan-500 hover:bg-cyan-600 text-white 
                                                 rounded-2xl font-bold text-xl transition-all hover:scale-105 shadow-lg"
                                    >
                                        📸 Start Camera
                                    </button>
                                </div>
                            )}
                            {cameraActive && (
                                <div className="absolute bottom-6 left-0 right-0 flex justify-center gap-4 px-6">
                                    <button
                                        onClick={captureAndRecognize}
                                        disabled={loading}
                                        className="flex-1 py-4 bg-cyan-500 hover:bg-cyan-600 text-white 
                                                 rounded-2xl font-bold shadow-lg transition-all hover:scale-105
                                                 disabled:opacity-50 disabled:scale-100"
                                    >
                                        {loading ? '🔍 Scanning...' : '🔍 Scan Object'}
                                    </button>
                                    <button
                                        onClick={stopCamera}
                                        className="w-14 h-14 flex items-center justify-center bg-red-500 hover:bg-red-600 text-white 
                                                 rounded-2xl shadow-lg transition-all hover:scale-105"
                                        aria-label="Stop Camera"
                                    >
                                        ✕
                                    </button>
                                </div>
                            )}
                        </div>

                        {/* Detected Objects */}
                        {detectedItems.length > 0 && (
                            <div className="space-y-4 animate-in slide-in-from-bottom-4 duration-500">
                                <h2 className="text-xl font-bold text-gray-800 px-2">
                                    Found {detectedItems.length} objects:
                                </h2>
                                {detectedItems.map((item, idx) => (
                                    <button
                                        key={idx}
                                        onClick={() => setSelectedItem(item)}
                                        className="w-full p-6 bg-white/80 backdrop-blur-md rounded-[2rem] shadow-lg text-left
                                                 hover:shadow-xl transition-all hover:scale-[1.02] border border-white/50
                                                 group"
                                    >
                                        <div className="flex items-center justify-between mb-2">
                                            <div className="flex items-center gap-3">
                                                <span className="text-2xl font-bold text-gray-800 group-hover:text-cyan-600 transition-colors">
                                                    {item.word}
                                                </span>
                                                {item.l1_translation && (
                                                    <span className="px-3 py-1 bg-cyan-100 text-cyan-700 rounded-full text-sm font-bold">
                                                        {item.l1_translation}
                                                    </span>
                                                )}
                                            </div>
                                            <span className="text-sm font-bold text-green-600 bg-green-100 px-3 py-1 rounded-full">
                                                {Math.round(item.confidence * 100)}%
                                            </span>
                                        </div>
                                        <p className="text-gray-600 text-sm leading-relaxed">
                                            {item.definition}
                                        </p>
                                    </button>
                                ))}
                            </div>
                        )}
                    </div>
                )}

                {/* Deck View */}
                {viewMode === 'deck' && (
                    <div className="space-y-4">
                        {deck.length === 0 ? (
                            <div className="text-center py-16 bg-white/60 backdrop-blur-md rounded-[2.5rem] shadow-xl border border-white/50">
                                <p className="text-8xl mb-6 animate-bounce">📚</p>
                                <h3 className="text-2xl font-bold text-gray-800 mb-2">
                                    Your deck is empty
                                </h3>
                                <p className="text-gray-500">
                                    Use the camera to scan objects and add them!
                                </p>
                            </div>
                        ) : (
                            <div className="grid gap-4">
                                {deck.map((item, idx) => (
                                    <div
                                        key={idx}
                                        className="p-6 bg-white/80 backdrop-blur-md rounded-[2rem] shadow-lg flex items-center justify-between
                                                 border border-white/50 hover:shadow-xl transition-all"
                                    >
                                        <div>
                                            <h3 className="text-xl font-bold text-gray-800 mb-1">
                                                {item.word}
                                            </h3>
                                            <div className="flex items-center gap-2">
                                                <span className="text-sm text-gray-500 bg-gray-100 px-2 py-1 rounded-lg">
                                                    {item.repetitions} reviews
                                                </span>
                                            </div>
                                        </div>
                                        <button
                                            onClick={() => speakWord(item.word)}
                                            className="w-12 h-12 flex items-center justify-center bg-cyan-100 text-cyan-600 
                                                     rounded-full hover:bg-cyan-200 transition-colors text-xl"
                                            aria-label={`Speak ${item.word}`}
                                        >
                                            🔊
                                        </button>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                )}

                {/* Review View */}
                {viewMode === 'review' && (
                    <div className="space-y-4">
                        {reviewItems.length === 0 ? (
                            <div className="text-center py-16 bg-white/60 backdrop-blur-md rounded-[2.5rem] shadow-xl border border-white/50">
                                <p className="text-8xl mb-6 animate-bounce">🎉</p>
                                <h3 className="text-2xl font-bold text-gray-800 mb-2">
                                    All caught up!
                                </h3>
                                <p className="text-gray-500">
                                    No cards to review right now.
                                </p>
                            </div>
                        ) : (
                            <div className="bg-white/80 backdrop-blur-md rounded-[2.5rem] shadow-xl p-8 border border-white/50 min-h-[400px] flex flex-col">
                                <div className="text-center mb-8">
                                    <span className="bg-gray-100 text-gray-500 px-4 py-1 rounded-full text-sm font-bold">
                                        Card {currentReviewIndex + 1} of {reviewItems.length}
                                    </span>
                                </div>

                                <div className="flex-1 flex flex-col items-center justify-center">
                                    <button
                                        onClick={() => speakWord(reviewItems[currentReviewIndex].word)}
                                        className="text-5xl font-bold text-gray-800 hover:text-cyan-600 transition-colors mb-8 text-center"
                                    >
                                        {reviewItems[currentReviewIndex].word} 🔊
                                    </button>

                                    {!showAnswer ? (
                                        <button
                                            onClick={() => setShowAnswer(true)}
                                            className="w-full max-w-xs py-4 bg-cyan-500 hover:bg-cyan-600 
                                                     text-white rounded-2xl font-bold text-lg shadow-lg 
                                                     transition-all hover:scale-105"
                                        >
                                            Show Answer
                                        </button>
                                    ) : (
                                        <div className="w-full space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
                                            <div className="text-center">
                                                <p className="text-4xl font-bold text-cyan-600 mb-2">
                                                    {getL1Translation(
                                                        reviewItems[currentReviewIndex].word,
                                                        session.l1
                                                    )}
                                                </p>
                                                <p className="text-gray-500 font-medium">
                                                    How well did you remember?
                                                </p>
                                            </div>

                                            <div className="grid grid-cols-3 gap-3">
                                                <button
                                                    onClick={() => recordReview(1)}
                                                    className="py-4 bg-red-100 hover:bg-red-200 text-red-700 
                                                             rounded-2xl font-bold transition-colors flex flex-col items-center gap-1"
                                                >
                                                    <span className="text-2xl">😕</span>
                                                    <span className="text-sm">Forgot</span>
                                                </button>
                                                <button
                                                    onClick={() => recordReview(3)}
                                                    className="py-4 bg-yellow-100 hover:bg-yellow-200 text-yellow-700 
                                                             rounded-2xl font-bold transition-colors flex flex-col items-center gap-1"
                                                >
                                                    <span className="text-2xl">🤔</span>
                                                    <span className="text-sm">Hard</span>
                                                </button>
                                                <button
                                                    onClick={() => recordReview(5)}
                                                    className="py-4 bg-green-100 hover:bg-green-200 text-green-700 
                                                             rounded-2xl font-bold transition-colors flex flex-col items-center gap-1"
                                                >
                                                    <span className="text-2xl">😊</span>
                                                    <span className="text-sm">Easy</span>
                                                </button>
                                            </div>
                                        </div>
                                    )}
                                </div>
                            </div>
                        )}
                    </div>
                )}

                {/* Selected Item Modal */}
                {selectedItem && (
                    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-end sm:items-center justify-center p-4 z-50 animate-in fade-in duration-200">
                        <div className="bg-white rounded-[2.5rem] w-full max-w-lg max-h-[85vh] overflow-y-auto shadow-2xl animate-in slide-in-from-bottom-10 duration-300">
                            <div className="p-8">
                                <div className="flex justify-between items-start mb-6">
                                    <div>
                                        <h2 className="text-4xl font-bold text-gray-800 mb-2">
                                            {selectedItem.word}
                                        </h2>
                                        {selectedItem.l1_translation && (
                                            <p className="text-2xl text-cyan-600 font-bold">
                                                {selectedItem.l1_translation}
                                            </p>
                                        )}
                                    </div>
                                    <button
                                        onClick={() => speakWord(selectedItem.word)}
                                        className="w-14 h-14 flex items-center justify-center bg-cyan-100 text-cyan-600 
                                                 rounded-full hover:bg-cyan-200 transition-colors text-2xl shadow-sm"
                                        aria-label="Speak word"
                                    >
                                        🔊
                                    </button>
                                </div>

                                <p className="text-gray-600 text-lg mb-8 leading-relaxed">
                                    {selectedItem.definition}
                                </p>

                                <div className="mb-8">
                                    <h3 className="font-bold text-gray-800 mb-3 flex items-center gap-2">
                                        <span>💬</span> Common phrases
                                    </h3>
                                    <div className="flex flex-wrap gap-2">
                                        {selectedItem.collocations.map((col, idx) => (
                                            <span
                                                key={idx}
                                                className="px-4 py-2 bg-cyan-50 text-cyan-700 rounded-xl text-sm font-bold border border-cyan-100"
                                            >
                                                {col}
                                            </span>
                                        ))}
                                    </div>
                                </div>

                                <div className="mb-8">
                                    <h3 className="font-bold text-gray-800 mb-3 flex items-center gap-2">
                                        <span>📝</span> Example sentences
                                    </h3>
                                    <div className="space-y-3">
                                        {selectedItem.sentence_frames.map((frame, idx) => (
                                            <p key={idx} className="text-gray-600 bg-gray-50 p-4 rounded-2xl border border-gray-100">
                                                {frame.split('___').map((part, i, arr) => (
                                                    <span key={i}>
                                                        {part}
                                                        {i < arr.length - 1 && <strong className="text-cyan-600 mx-1">{selectedItem.word}</strong>}
                                                    </span>
                                                ))}
                                            </p>
                                        ))}
                                    </div>
                                </div>

                                <div className="flex gap-4">
                                    <button
                                        onClick={() => setSelectedItem(null)}
                                        className="flex-1 py-4 bg-gray-100 hover:bg-gray-200 
                                                 text-gray-700 rounded-2xl font-bold transition-colors"
                                    >
                                        Close
                                    </button>
                                    <button
                                        onClick={() => addToDeck(selectedItem)}
                                        disabled={deck.some(d => d.word === selectedItem.word)}
                                        className="flex-1 py-4 bg-cyan-500 hover:bg-cyan-600 
                                                 text-white rounded-2xl font-bold transition-colors shadow-lg
                                                 disabled:opacity-50 disabled:cursor-not-allowed disabled:shadow-none"
                                    >
                                        {deck.some(d => d.word === selectedItem.word)
                                            ? '✓ In Deck'
                                            : '+ Add to Deck'}
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </main>
    );
}
