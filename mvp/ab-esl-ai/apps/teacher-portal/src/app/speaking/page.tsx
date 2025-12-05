"use client";

import { useState, useEffect } from "react";
import { Mic, Volume2, ArrowRight, CheckCircle, AlertCircle, Languages, Sparkles, Play } from 'lucide-react';

interface Exercise {
    pair_id: string;
    sounds: string[];
    difficulty: string;
    sample_words: Array<{
        word1: string;
        word2: string;
        context: string;
    }>;
}

export default function SpeakingPage() {
    const [l1Language, setL1Language] = useState("es");
    const [exercises, setExercises] = useState<Exercise[]>([]);
    const [currentExercise, setCurrentExercise] = useState<Exercise | null>(null);
    const [currentWordPair, setCurrentWordPair] = useState(0);
    const [word1Input, setWord1Input] = useState("");
    const [word2Input, setWord2Input] = useState("");
    const [results, setResults] = useState<any>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

    const languages = [
        { code: "ar", name: "Arabic" },
        { code: "es", name: "Spanish" },
        { code: "zh", name: "Chinese" },
        { code: "fr", name: "French" },
        { code: "ko", name: "Korean" },
    ];

    const loadExercises = async () => {
        setLoading(true);
        setError("");

        try {
            const res = await fetch(
                `${API_URL}/v1/speaking/exercises/${l1Language}`
            );
            if (!res.ok) throw new Error("Failed to load exercises");
            const data = await res.json();
            setExercises(data.exercises || []);

            if (data.exercises && data.exercises.length > 0) {
                setCurrentExercise(data.exercises[0]);
                setCurrentWordPair(0);
            }
        } catch (err: any) {
            setError(err.message || "Failed to load exercises");
        } finally {
            setLoading(false);
        }
    };

    const scorePronunciation = async () => {
        if (!currentExercise || !word1Input || !word2Input) {
            setError("Please type both words");
            return;
        }

        setLoading(true);
        setError("");

        try {
            const res = await fetch(`${API_URL}/v1/speaking/score_minimal_pair`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    word1: word1Input,
                    word2: word2Input,
                    pair_id: currentExercise.pair_id,
                }),
            });

            if (!res.ok) throw new Error("Failed to score");
            const data = await res.json();
            setResults(data);
        } catch (err: any) {
            setError(err.message || "Failed to score pronunciation");
        } finally {
            setLoading(false);
        }
    };

    const nextPair = () => {
        if (!currentExercise) return;

        if (currentWordPair < currentExercise.sample_words.length - 1) {
            setCurrentWordPair(currentWordPair + 1);
        } else {
            // Move to next exercise
            const currentIdx = exercises.findIndex(e => e.pair_id === currentExercise.pair_id);
            if (currentIdx < exercises.length - 1) {
                setCurrentExercise(exercises[currentIdx + 1]);
                setCurrentWordPair(0);
            }
        }

        // Reset inputs and results
        setWord1Input("");
        setWord2Input("");
        setResults(null);
    };

    const getScoreColor = (score: number) => {
        if (score >= 0.9) return "text-green-600 bg-green-50 border-green-200";
        if (score >= 0.7) return "text-yellow-600 bg-yellow-50 border-yellow-200";
        return "text-red-600 bg-red-50 border-red-200";
    };

    const getDifficultyColor = (difficulty: string) => {
        if (difficulty === "easy") return "bg-green-100 text-green-800 border-green-200";
        if (difficulty === "medium") return "bg-yellow-100 text-yellow-800 border-yellow-200";
        return "bg-red-100 text-red-800 border-red-200";
    };

    useEffect(() => {
        loadExercises();
    }, [l1Language]);

    const currentWord = currentExercise?.sample_words[currentWordPair];

    return (
        <div className="min-h-screen bg-gray-50 p-8">
            <div className="max-w-5xl mx-auto space-y-8">
                {/* Header */}
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                    <div>
                        <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
                            <Mic className="w-8 h-8 text-indigo-600" />
                            Speaking Coach
                        </h1>
                        <p className="mt-2 text-gray-500">
                            Practice pronunciation with targeted minimal pairs
                        </p>
                    </div>
                    
                    {/* Language Selection */}
                    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-2 flex items-center gap-3">
                        <div className="p-2 bg-indigo-50 rounded-lg">
                            <Languages className="w-5 h-5 text-indigo-600" />
                        </div>
                        <select
                            value={l1Language}
                            onChange={(e) => setL1Language(e.target.value)}
                            className="bg-transparent border-none text-gray-700 font-medium focus:ring-0 cursor-pointer pr-8"
                            title="Select your native language"
                            aria-label="Select your native language"
                        >
                            {languages.map((lang) => (
                                <option key={lang.code} value={lang.code}>
                                    {lang.name}
                                </option>
                            ))}
                        </select>
                    </div>
                </div>

                {error && (
                    <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg flex items-center gap-2">
                        <AlertCircle className="w-5 h-5" />
                        {error}
                    </div>
                )}

                {/* Current Exercise */}
                {currentExercise && currentWord && (
                    <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
                        <div className="p-6 border-b border-gray-100 flex justify-between items-center bg-gray-50/50">
                            <div>
                                <h2 className="text-xl font-bold text-gray-900 flex items-center gap-2">
                                    Sound Contrast: <span className="text-indigo-600">{currentExercise.sounds.join(" vs ")}</span>
                                </h2>
                                <p className="text-sm text-gray-500 mt-1">
                                    Exercise {currentWordPair + 1} of {currentExercise.sample_words.length}
                                </p>
                            </div>
                            <span
                                className={`px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider border ${getDifficultyColor(
                                    currentExercise.difficulty
                                )}`}
                            >
                                {currentExercise.difficulty}
                            </span>
                        </div>

                        <div className="p-8">
                            {/* Practice Words */}
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
                                <div className="bg-blue-50 rounded-xl p-8 text-center border border-blue-100 hover:border-blue-200 transition-colors group">
                                    <div className="text-sm font-bold text-blue-600 uppercase tracking-wider mb-4">Word 1</div>
                                    <div className="text-4xl font-bold text-gray-900 mb-6 group-hover:scale-105 transition-transform">
                                        {currentWord.word1}
                                    </div>
                                    <div className="relative">
                                        <input
                                            type="text"
                                            placeholder="Type what you said..."
                                            value={word1Input}
                                            onChange={(e) => setWord1Input(e.target.value)}
                                            className="w-full border border-blue-200 rounded-lg p-3 text-center focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all bg-white shadow-sm"
                                        />
                                        <div className="absolute right-3 top-3 text-gray-400">
                                            <Mic className="w-5 h-5" />
                                        </div>
                                    </div>
                                </div>

                                <div className="bg-purple-50 rounded-xl p-8 text-center border border-purple-100 hover:border-purple-200 transition-colors group">
                                    <div className="text-sm font-bold text-purple-600 uppercase tracking-wider mb-4">Word 2</div>
                                    <div className="text-4xl font-bold text-gray-900 mb-6 group-hover:scale-105 transition-transform">
                                        {currentWord.word2}
                                    </div>
                                    <div className="relative">
                                        <input
                                            type="text"
                                            placeholder="Type what you said..."
                                            value={word2Input}
                                            onChange={(e) => setWord2Input(e.target.value)}
                                            className="w-full border border-purple-200 rounded-lg p-3 text-center focus:ring-2 focus:ring-purple-500 focus:border-purple-500 outline-none transition-all bg-white shadow-sm"
                                        />
                                        <div className="absolute right-3 top-3 text-gray-400">
                                            <Mic className="w-5 h-5" />
                                        </div>
                                    </div>
                                </div>
                            </div>

                            {/* Context */}
                            <div className="bg-gray-50 border border-gray-200 rounded-xl p-6 mb-8">
                                <div className="flex items-start gap-3">
                                    <div className="p-2 bg-white rounded-lg border border-gray-200 shadow-sm">
                                        <Volume2 className="w-5 h-5 text-gray-600" />
                                    </div>
                                    <div>
                                        <div className="text-sm font-bold text-gray-900 mb-1">
                                            Example Context
                                        </div>
                                        <div className="text-gray-600 italic text-lg leading-relaxed">"{currentWord.context}"</div>
                                    </div>
                                </div>
                            </div>

                            {/* Action Buttons */}
                            <div className="flex gap-4">
                                <button
                                    onClick={scorePronunciation}
                                    disabled={loading || !word1Input || !word2Input}
                                    className="flex-1 bg-indigo-600 text-white font-bold py-4 rounded-xl hover:bg-indigo-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-sm flex items-center justify-center gap-2"
                                >
                                    {loading ? (
                                        <>
                                            <Sparkles className="w-5 h-5 animate-spin" />
                                            Scoring...
                                        </>
                                    ) : (
                                        <>
                                            <CheckCircle className="w-5 h-5" />
                                            Check Pronunciation
                                        </>
                                    )}
                                </button>
                                <button
                                    onClick={nextPair}
                                    className="px-8 bg-white border border-gray-200 text-gray-700 font-bold py-4 rounded-xl hover:bg-gray-50 transition-all shadow-sm flex items-center gap-2"
                                >
                                    Next Pair <ArrowRight className="w-5 h-5" />
                                </button>
                            </div>

                            {/* Results */}
                            {results && (
                                <div className="mt-8 bg-white rounded-xl border border-gray-200 overflow-hidden animate-in fade-in slide-in-from-bottom-4 duration-500">
                                    <div className="bg-indigo-50 p-4 border-b border-indigo-100 flex justify-between items-center">
                                        <h3 className="font-bold text-indigo-900 flex items-center gap-2">
                                            <Sparkles className="w-5 h-5 text-indigo-600" />
                                            Analysis Results
                                        </h3>
                                        <div className="text-sm font-bold text-indigo-700 bg-white px-3 py-1 rounded-full shadow-sm">
                                            Overall Score: {(results.average_score * 100).toFixed(0)}%
                                        </div>
                                    </div>

                                    <div className="p-6">
                                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                                            {/* Word 1 Result */}
                                            <div className="bg-gray-50 rounded-xl p-5 border border-gray-100">
                                                <div className="flex justify-between items-start mb-4">
                                                    <div className="text-sm font-bold text-gray-500 uppercase tracking-wider">
                                                        {currentWord.word1}
                                                    </div>
                                                    <div
                                                        className={`text-lg font-bold px-3 py-1 rounded-lg border ${getScoreColor(
                                                            results.word1.score
                                                        )}`}
                                                    >
                                                        {(results.word1.score * 100).toFixed(0)}%
                                                    </div>
                                                </div>
                                                <div className="space-y-2">
                                                    <div className="text-sm text-gray-600">
                                                        You said: <strong className="text-gray-900 bg-white px-2 py-0.5 rounded border border-gray-200">{results.word1.transcribed}</strong>
                                                    </div>
                                                    <div className="text-sm text-gray-600 leading-relaxed">
                                                        {results.word1.feedback}
                                                    </div>
                                                </div>
                                            </div>

                                            {/* Word 2 Result */}
                                            <div className="bg-gray-50 rounded-xl p-5 border border-gray-100">
                                                <div className="flex justify-between items-start mb-4">
                                                    <div className="text-sm font-bold text-gray-500 uppercase tracking-wider">
                                                        {currentWord.word2}
                                                    </div>
                                                    <div
                                                        className={`text-lg font-bold px-3 py-1 rounded-lg border ${getScoreColor(
                                                            results.word2.score
                                                        )}`}
                                                    >
                                                        {(results.word2.score * 100).toFixed(0)}%
                                                    </div>
                                                </div>
                                                <div className="space-y-2">
                                                    <div className="text-sm text-gray-600">
                                                        You said: <strong className="text-gray-900 bg-white px-2 py-0.5 rounded border border-gray-200">{results.word2.transcribed}</strong>
                                                    </div>
                                                    <div className="text-sm text-gray-600 leading-relaxed">
                                                        {results.word2.feedback}
                                                    </div>
                                                </div>
                                            </div>
                                        </div>

                                        {/* Overall Feedback */}
                                        <div className="bg-blue-50 border border-blue-100 p-5 rounded-xl flex gap-4">
                                            <div className="p-2 bg-white rounded-lg h-fit border border-blue-100 shadow-sm">
                                                <MessageSquare className="w-5 h-5 text-blue-600" />
                                            </div>
                                            <div>
                                                <div className="font-bold text-blue-900 mb-1">Feedback</div>
                                                <div className="text-blue-800 leading-relaxed text-sm">{results.overall_feedback}</div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>
                )}

                {!currentExercise && !loading && (
                    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-12 text-center">
                        <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                            <AlertCircle className="w-8 h-8 text-gray-400" />
                        </div>
                        <h3 className="text-lg font-bold text-gray-900 mb-2">
                            No exercises found for {l1Language.toUpperCase()} speakers
                        </h3>
                        <p className="text-gray-500">
                            Try selecting a different native language above.
                        </p>
                    </div>
                )}

                {/* Instructions */}
                <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                    <h3 className="font-bold text-gray-900 mb-4 flex items-center gap-2">
                        <div className="p-2 bg-green-100 rounded-lg">
                            <Play className="w-4 h-4 text-green-600" />
                        </div>
                        How to Practice
                    </h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        {[
                            'Listen carefully to the sound difference between the two words',
                            'Practice saying both words out loud',
                            'Type what you think you said (simulates ASR transcription)',
                            'Click "Check Pronunciation" to get feedback',
                            'Green = Excellent, Yellow = Close, Red = Needs practice',
                            'Focus on consistent distinction between the sounds'
                        ].map((step, i) => (
                            <div key={i} className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg border border-gray-100">
                                <div className="w-6 h-6 rounded-full bg-white border border-gray-200 flex items-center justify-center text-xs font-bold text-gray-500 flex-shrink-0 shadow-sm">
                                    {i + 1}
                                </div>
                                <p className="text-sm text-gray-600 font-medium">{step}</p>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
}

// Helper component for icons
function MessageSquare({ className }: { className?: string }) {
    return (
        <svg 
            xmlns="http://www.w3.org/2000/svg" 
            width="24" 
            height="24" 
            viewBox="0 0 24 24" 
            fill="none" 
            stroke="currentColor" 
            strokeWidth="2" 
            strokeLinecap="round" 
            strokeLinejoin="round" 
            className={className}
        >
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
        </svg>
    );
}
