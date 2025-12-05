'use client';

import { useEffect, useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';

interface SessionData {
    token: string;
    sessionId: number;
    participantId: number;
    nickname: string;
    l1: string;
}

interface VocabWord {
    en: string;
    l1: string;
    category: string;
    definition?: string;
}

// L1 translations for common vocabulary
const L1_VOCABULARY: Record<string, Record<string, string>> = {
    ar: {
        book: 'كتاب', pencil: 'قلم رصاص', desk: 'مكتب', teacher: 'معلم', student: 'طالب',
        chair: 'كرسي', board: 'لوحة', paper: 'ورقة', read: 'اقرأ', write: 'اكتب',
        listen: 'استمع', open: 'افتح', close: 'أغلق', sit: 'اجلس', stand: 'قف', help: 'ساعد',
        one: 'واحد', two: 'اثنان', three: 'ثلاثة', four: 'أربعة', five: 'خمسة',
        six: 'ستة', seven: 'سبعة', eight: 'ثمانية', nine: 'تسعة', ten: 'عشرة',
    },
    es: {
        book: 'libro', pencil: 'lápiz', desk: 'escritorio', teacher: 'maestro', student: 'estudiante',
        chair: 'silla', board: 'pizarra', paper: 'papel', read: 'leer', write: 'escribir',
        listen: 'escuchar', open: 'abrir', close: 'cerrar', sit: 'sentarse', stand: 'pararse', help: 'ayudar',
        one: 'uno', two: 'dos', three: 'tres', four: 'cuatro', five: 'cinco',
        six: 'seis', seven: 'siete', eight: 'ocho', nine: 'nueve', ten: 'diez',
    },
    zh: {
        book: '书', pencil: '铅笔', desk: '课桌', teacher: '老师', student: '学生',
        chair: '椅子', board: '黑板', paper: '纸', read: '读', write: '写',
        listen: '听', open: '打开', close: '关闭', sit: '坐', stand: '站', help: '帮助',
        one: '一', two: '二', three: '三', four: '四', five: '五',
        six: '六', seven: '七', eight: '八', nine: '九', ten: '十',
    },
    vi: {
        book: 'sách', pencil: 'bút chì', desk: 'bàn', teacher: 'giáo viên', student: 'học sinh',
        chair: 'ghế', board: 'bảng', paper: 'giấy', read: 'đọc', write: 'viết',
        listen: 'nghe', open: 'mở', close: 'đóng', sit: 'ngồi', stand: 'đứng', help: 'giúp đỡ',
        one: 'một', two: 'hai', three: 'ba', four: 'bốn', five: 'năm',
        six: 'sáu', seven: 'bảy', eight: 'tám', nine: 'chín', ten: 'mười',
    },
    ko: {
        book: '책', pencil: '연필', desk: '책상', teacher: '선생님', student: '학생',
        chair: '의자', board: '칠판', paper: '종이', read: '읽다', write: '쓰다',
        listen: '듣다', open: '열다', close: '닫다', sit: '앉다', stand: '서다', help: '돕다',
        one: '하나', two: '둘', three: '셋', four: '넷', five: '다섯',
        six: '여섯', seven: '일곱', eight: '여덟', nine: '아홉', ten: '열',
    },
    tl: {
        book: 'libro', pencil: 'lapis', desk: 'mesa', teacher: 'guro', student: 'estudyante',
        chair: 'upuan', board: 'pisara', paper: 'papel', read: 'magbasa', write: 'magsulat',
        listen: 'makinig', open: 'buksan', close: 'isara', sit: 'umupo', stand: 'tumayo', help: 'tulong',
        one: 'isa', two: 'dalawa', three: 'tatlo', four: 'apat', five: 'lima',
        six: 'anim', seven: 'pito', eight: 'walo', nine: 'siyam', ten: 'sampu',
    },
    fr: {
        book: 'livre', pencil: 'crayon', desk: 'bureau', teacher: 'professeur', student: 'élève',
        chair: 'chaise', board: 'tableau', paper: 'papier', read: 'lire', write: 'écrire',
        listen: 'écouter', open: 'ouvrir', close: 'fermer', sit: 's\'asseoir', stand: 'se lever', help: 'aider',
        one: 'un', two: 'deux', three: 'trois', four: 'quatre', five: 'cinq',
        six: 'six', seven: 'sept', eight: 'huit', nine: 'neuf', ten: 'dix',
    },
    hi: {
        book: 'किताब', pencil: 'पेंसिल', desk: 'डेस्क', teacher: 'शिक्षक', student: 'छात्र',
        chair: 'कुर्सी', board: 'बोर्ड', paper: 'कागज', read: 'पढ़ना', write: 'लिखना',
        listen: 'सुनना', open: 'खोलना', close: 'बंद करना', sit: 'बैठना', stand: 'खड़ा होना', help: 'मदद',
        one: 'एक', two: 'दो', three: 'तीन', four: 'चार', five: 'पाँच',
        six: 'छह', seven: 'सात', eight: 'आठ', nine: 'नौ', ten: 'दस',
    },
    pa: {
        book: 'ਕਿਤਾਬ', pencil: 'ਪੈਨਸਿਲ', desk: 'ਮੇਜ਼', teacher: 'ਅਧਿਆਪਕ', student: 'ਵਿਦਿਆਰਥੀ',
        chair: 'ਕੁਰਸੀ', board: 'ਬੋਰਡ', paper: 'ਕਾਗਜ਼', read: 'ਪੜ੍ਹੋ', write: 'ਲਿਖੋ',
        listen: 'ਸੁਣੋ', open: 'ਖੋਲ੍ਹੋ', close: 'ਬੰਦ ਕਰੋ', sit: 'ਬੈਠੋ', stand: 'ਖੜ੍ਹੇ ਹੋਵੋ', help: 'ਮਦਦ',
        one: 'ਇੱਕ', two: 'ਦੋ', three: 'ਤਿੰਨ', four: 'ਚਾਰ', five: 'ਪੰਜ',
        six: 'ਛੇ', seven: 'ਸੱਤ', eight: 'ਅੱਠ', nine: 'ਨੌਂ', ten: 'ਦਸ',
    },
    ur: {
        book: 'کتاب', pencil: 'پنسل', desk: 'میز', teacher: 'استاد', student: 'طالب علم',
        chair: 'کرسی', board: 'بورڈ', paper: 'کاغذ', read: 'پڑھنا', write: 'لکھنا',
        listen: 'سننا', open: 'کھولنا', close: 'بند کرنا', sit: 'بیٹھنا', stand: 'کھڑا ہونا', help: 'مدد',
        one: 'ایک', two: 'دو', three: 'تین', four: 'چار', five: 'پانچ',
        six: 'چھ', seven: 'سات', eight: 'آٹھ', nine: 'نو', ten: 'دس',
    },
    so: {
        book: 'buug', pencil: 'qalin', desk: 'miis', teacher: 'macalin', student: 'arday',
        chair: 'kursi', board: 'sabuurad', paper: 'warqad', read: 'akhri', write: 'qor',
        listen: 'dhageyso', open: 'fur', close: 'xir', sit: 'fadhiiso', stand: 'istaag', help: 'caawi',
        one: 'kow', two: 'laba', three: 'saddex', four: 'afar', five: 'shan',
        six: 'lix', seven: 'todoba', eight: 'siddeed', nine: 'sagaal', ten: 'toban',
    },
};

const BASE_VOCABULARY: Record<string, string[]> = {
    classroom: ['book', 'pencil', 'desk', 'teacher', 'student', 'chair', 'board', 'paper'],
    actions: ['read', 'write', 'listen', 'open', 'close', 'sit', 'stand', 'help'],
    numbers: ['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight'],
};

const categories = [
    { id: 'classroom', name: 'Classroom', emoji: '🏫' },
    { id: 'actions', name: 'Actions', emoji: '✋' },
    { id: 'numbers', name: 'Numbers', emoji: '🔢' },
];

export default function VocabularyPage() {
    const router = useRouter();
    const [session, setSession] = useState<SessionData | null>(null);
    const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
    const [currentIndex, setCurrentIndex] = useState(0);
    const [showAnswer, setShowAnswer] = useState(false);
    const [score, setScore] = useState({ correct: 0, total: 0 });
    const [vocabulary, setVocabulary] = useState<Record<string, VocabWord[]>>({});

    const loadTranslations = useCallback((l1: string) => {
        const translations = L1_VOCABULARY[l1] || {};
        const newVocab: Record<string, VocabWord[]> = {};

        Object.entries(BASE_VOCABULARY).forEach(([category, words]) => {
            newVocab[category] = words.map(word => ({
                en: word,
                l1: translations[word] || '',
                category,
            }));
        });

        setVocabulary(newVocab);
    }, []);

    useEffect(() => {
        const stored = localStorage.getItem('session');
        if (!stored) {
            router.push('/');
            return;
        }
        const sessionData = JSON.parse(stored);
        setSession(sessionData);
        loadTranslations(sessionData.l1);
    }, [router, loadTranslations]);

    const speakWord = (word: string) => {
        const utterance = new SpeechSynthesisUtterance(word);
        utterance.lang = 'en-US';
        utterance.rate = 0.8;
        speechSynthesis.speak(utterance);
    };

    const handleKnew = () => {
        setScore({ correct: score.correct + 1, total: score.total + 1 });
        nextWord();
    };

    const handleDidNotKnow = () => {
        setScore({ correct: score.correct, total: score.total + 1 });
        nextWord();
    };

    const nextWord = () => {
        const words = vocabulary[selectedCategory || 'classroom'];
        if (currentIndex < words.length - 1) {
            setCurrentIndex(currentIndex + 1);
            setShowAnswer(false);
        } else {
            // Show final score
        }
    };

    const resetCategory = () => {
        setCurrentIndex(0);
        setShowAnswer(false);
        setScore({ correct: 0, total: 0 });
        setSelectedCategory(null);
    };

    if (!session) {
        return (
            <div className="min-h-screen flex items-center justify-center">
                <div className="animate-pulse text-2xl">Loading...</div>
            </div>
        );
    }

    const currentWords = selectedCategory ? vocabulary[selectedCategory] : [];
    const currentWord = currentWords[currentIndex];
    const isComplete = selectedCategory && currentIndex >= currentWords.length - 1 && score.total > 0;

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
                    <h1 className="text-xl font-bold text-gray-800">Vocabulary</h1>
                    <div className="w-10" />
                </div>
            </header>

            <div className="max-w-md mx-auto p-4 relative z-0">
                {/* Category Selection */}
                {!selectedCategory && (
                    <div className="space-y-6 animate-slide-up">
                        <div className="text-center mb-8">
                            <span className="text-6xl mb-4 block">📝</span>
                            <h2 className="text-2xl font-bold text-gray-800 mb-2">
                                Word Practice
                            </h2>
                            <p className="text-gray-500">Choose a topic to learn new words.</p>
                        </div>

                        <div className="grid gap-4">
                            {categories.map((cat) => (
                                <button
                                    key={cat.id}
                                    onClick={() => setSelectedCategory(cat.id)}
                                    className="w-full bg-white p-6 rounded-3xl shadow-lg border border-gray-100 text-left
                       hover:shadow-xl hover:scale-[1.02] transition-all active:scale-95
                       flex items-center gap-6 group"
                                >
                                    <span className="text-5xl group-hover:scale-110 transition-transform">{cat.emoji}</span>
                                    <div>
                                        <h3 className="text-xl font-bold text-gray-800 mb-1">{cat.name}</h3>
                                        <p className="text-indigo-500 font-bold text-sm bg-indigo-50 px-3 py-1 rounded-full inline-block">
                                            {vocabulary[cat.id]?.length || 0} words
                                        </p>
                                    </div>
                                    <div className="ml-auto text-gray-300 text-2xl group-hover:text-indigo-400 transition-colors">
                                        →
                                    </div>
                                </button>
                            ))}
                        </div>
                    </div>
                )}

                {/* Flashcard View */}
                {selectedCategory && !isComplete && currentWord && (
                    <div className="animate-slide-up pt-4">
                        {/* Progress */}
                        <div className="flex items-center justify-between mb-8 bg-white p-4 rounded-2xl shadow-sm border border-gray-100">
                            <span className="text-gray-500 font-bold text-sm">
                                Word {currentIndex + 1} of {currentWords.length}
                            </span>
                            <div className="flex-1 mx-4 h-3 bg-gray-100 rounded-full overflow-hidden">
                                {/* eslint-disable-next-line react/forbid-dom-props */}
                                <div
                                    className="h-full bg-gradient-to-r from-indigo-400 to-purple-400 transition-all duration-500 ease-out rounded-full"
                                    style={{ width: `${((currentIndex + 1) / currentWords.length) * 100}%` }}
                                />
                            </div>
                            <span className="text-green-600 font-bold bg-green-50 px-3 py-1 rounded-full text-sm">
                                {score.correct} Correct
                            </span>
                        </div>

                        {/* Card */}
                        <div className="perspective-1000 relative min-h-[400px]">
                            <div
                                className={`bg-white rounded-[2.5rem] shadow-xl p-8 text-center min-h-[400px]
                     flex flex-col items-center justify-center cursor-pointer border border-gray-100
                     transition-all duration-500 transform relative overflow-hidden
                     ${showAnswer ? 'ring-4 ring-indigo-100' : 'hover:shadow-2xl hover:-translate-y-1'}`}
                                onClick={() => !showAnswer && setShowAnswer(true)}
                            >
                                {/* Decorative background blob */}
                                <div className="absolute top-0 left-0 w-full h-32 bg-gradient-to-b from-indigo-50 to-transparent opacity-50 pointer-events-none" />

                                <div className="relative z-10 w-full">
                                    <div className="text-6xl font-black text-gray-800 mb-8 tracking-tight">
                                        {currentWord.en}
                                    </div>

                                    <button
                                        onClick={(e) => {
                                            e.stopPropagation();
                                            speakWord(currentWord.en);
                                        }}
                                        className="w-16 h-16 bg-indigo-100 hover:bg-indigo-200 text-indigo-600 rounded-full flex items-center justify-center mx-auto mb-8 transition-all active:scale-95 shadow-sm"
                                        aria-label="Listen to word"
                                    >
                                        <span className="text-2xl">🔊</span>
                                    </button>

                                    {!showAnswer ? (
                                        <div className="animate-pulse text-gray-400 font-bold mt-8">
                                            Tap card to reveal meaning
                                        </div>
                                    ) : (
                                        <div className="animate-slide-up w-full">
                                            <div className="text-3xl text-gray-600 font-bold mb-8 pb-8 border-b border-gray-100">
                                                {/* In a real app, we'd show the L1 translation here if available */}
                                                Do you know this word?
                                            </div>
                                            <div className="flex gap-4">
                                                <button
                                                    onClick={(e) => {
                                                        e.stopPropagation();
                                                        handleDidNotKnow();
                                                    }}
                                                    className="flex-1 bg-red-50 hover:bg-red-100 text-red-600 border-2 border-red-100
                                         font-bold py-4 rounded-2xl transition-all active:scale-95 text-lg flex flex-col items-center gap-1"
                                                >
                                                    <span className="text-2xl">❌</span>
                                                    <span>No</span>
                                                </button>
                                                <button
                                                    onClick={(e) => {
                                                        e.stopPropagation();
                                                        handleKnew();
                                                    }}
                                                    className="flex-1 bg-green-50 hover:bg-green-100 text-green-600 border-2 border-green-100
                                         font-bold py-4 rounded-2xl transition-all active:scale-95 text-lg flex flex-col items-center gap-1"
                                                >
                                                    <span className="text-2xl">✅</span>
                                                    <span>Yes!</span>
                                                </button>
                                            </div>
                                        </div>
                                    )}
                                </div>
                            </div>
                        </div>

                        <button
                            onClick={resetCategory}
                            className="mt-8 text-gray-400 hover:text-gray-600 font-bold w-full text-center py-4"
                        >
                            Quit Practice
                        </button>
                    </div>
                )}

                {/* Results */}
                {isComplete && (
                    <div className="animate-slide-up text-center pt-8">
                        <div className="bg-white rounded-[2.5rem] shadow-xl p-10 mb-8 border border-gray-100 relative overflow-hidden">
                            <div className={`absolute top-0 left-0 w-full h-2 ${score.correct === score.total ? 'bg-green-500' : 'bg-indigo-500'}`} />

                            <div className="text-8xl mb-6 animate-bounce-slow">
                                {score.correct === score.total ? '🌟' : score.correct >= score.total * 0.7 ? '👍' : '💪'}
                            </div>

                            <h2 className="text-3xl font-black text-gray-800 mb-2">
                                Great Job!
                            </h2>
                            <p className="text-gray-500 font-medium mb-8">You've completed this set.</p>

                            <div className="bg-gray-50 rounded-3xl p-6 mb-2">
                                <div className="text-6xl font-black text-indigo-600 mb-2">
                                    {score.correct} <span className="text-3xl text-gray-400 font-bold">/ {score.total}</span>
                                </div>
                                <p className="text-gray-500 font-bold uppercase tracking-wide text-sm">Words Mastered</p>
                            </div>
                        </div>

                        <div className="grid gap-4">
                            <button
                                onClick={() => {
                                    setCurrentIndex(0);
                                    setShowAnswer(false);
                                    setScore({ correct: 0, total: 0 });
                                }}
                                className="w-full bg-indigo-600 hover:bg-indigo-700 text-white
                       font-bold py-4 rounded-2xl shadow-lg shadow-indigo-200 transition-all active:scale-95 text-lg"
                            >
                                🔄 Practice Again
                            </button>
                            <button
                                onClick={resetCategory}
                                className="w-full bg-white hover:bg-gray-50 text-gray-700 border-2 border-gray-100
                       font-bold py-4 rounded-2xl transition-all active:scale-95 text-lg"
                            >
                                📚 Choose New Topic
                            </button>
                        </div>
                    </div>
                )}
            </div>
        </main>
    );
}
