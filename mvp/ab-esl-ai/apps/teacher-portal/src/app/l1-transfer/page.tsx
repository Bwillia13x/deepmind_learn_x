"use client";

import { useState } from 'react';
import { Globe, AlertTriangle, Lightbulb, BookOpen, ArrowRight, CheckCircle } from 'lucide-react';

const LANGUAGES = [
    { code: 'ar', name: 'Arabic', flag: '🇸🇦' },
    { code: 'zh', name: 'Chinese (Mandarin)', flag: '🇨🇳' },
    { code: 'es', name: 'Spanish', flag: '🇪��' },
    { code: 'ko', name: 'Korean', flag: '🇰��' },
    { code: 'tl', name: 'Tagalog', flag: '🇵🇭' },
    { code: 'pa', name: 'Punjabi', flag: '��🇳' },
    { code: 'uk', name: 'Ukrainian', flag: '🇺🇦' },
    { code: 'so', name: 'Somali', flag: '🇸🇴' },
    { code: 'vi', name: 'Vietnamese', flag: '🇻🇳' },
    { code: 'fa', name: 'Farsi/Dari', flag: '🇮🇷' },
    { code: 'hi', name: 'Hindi', flag: '🇮🇳' },
    { code: 'ur', name: 'Urdu', flag: '🇵🇰' },
    { code: 'fr', name: 'French', flag: '🇫🇷' },
];

interface TransferPattern {
    phonology: {
        difficult_sounds: string[];
        substitution_patterns: Record<string, string>;
        teaching_strategies: string[];
    };
    grammar: {
        challenges: string[];
        transfer_errors: string[];
        focus_areas: string[];
    };
    vocabulary: {
        cognates: string[];
        false_friends: string[];
        strategies: string[];
    };
    cultural_considerations: string[];
}

interface Exercise {
    type: string;
    instruction: string;
    examples?: string[];
}

export default function L1TransferPage() {
    const [selectedL1, setSelectedL1] = useState('ar');
    const [patterns, setPatterns] = useState<TransferPattern | null>(null);
    const [loading, setLoading] = useState(false);
    const [studentText, setStudentText] = useState('');
    const [predictedErrors, setPredictedErrors] = useState<string[]>([]);
    const [exercises, setExercises] = useState<Exercise[]>([]);

    const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

    const fetchPatterns = async () => {
        setLoading(true);
        try {
            const res = await fetch(`${API_URL}/v1/l1-transfer/patterns/${selectedL1}`);
            if (res.ok) {
                const data = await res.json();
                setPatterns(data);
            }
        } catch (error) {
            console.error('Error fetching patterns:', error);
        }
        setLoading(false);
    };

    const predictErrors = async () => {
        if (!studentText.trim()) return;
        setLoading(true);
        try {
            const res = await fetch(`${API_URL}/v1/l1-transfer/predict-errors`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ l1_code: selectedL1, text: studentText }),
            });
            if (res.ok) {
                const data = await res.json();
                setPredictedErrors(data.predicted_errors || []);
            }
        } catch (error) {
            console.error('Error predicting errors:', error);
        }
        setLoading(false);
    };

    const generateExercises = async () => {
        setLoading(true);
        try {
            const res = await fetch(`${API_URL}/v1/l1-transfer/generate-exercises`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ l1_code: selectedL1, focus_areas: ['phonology', 'grammar'] }),
            });
            if (res.ok) {
                const data = await res.json();
                setExercises(data.exercises || []);
            }
        } catch (error) {
            console.error('Error generating exercises:', error);
        }
        setLoading(false);
    };

    const selectedLang = LANGUAGES.find(l => l.code === selectedL1);

    return (
        <div className="min-h-screen bg-gray-50 p-8">
            <div className="max-w-7xl mx-auto space-y-8">
                {/* Header */}
                <div>
                    <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
                        <Globe className="w-8 h-8 text-indigo-600" />
                        L1 Transfer Intelligence
                    </h1>
                    <p className="mt-2 text-gray-500">
                        Understand how a student&apos;s first language affects their English learning journey.
                    </p>
                </div>

                {/* Language Selector */}
                <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                    <h2 className="text-lg font-bold text-gray-900 mb-4">Select Student&apos;s First Language (L1)</h2>
                    <div className="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-5 lg:grid-cols-7 gap-3">
                        {LANGUAGES.map((lang) => (
                            <button
                                key={lang.code}
                                onClick={() => {
                                    setSelectedL1(lang.code);
                                    setPatterns(null);
                                }}
                                className={`p-3 rounded-xl border transition-all text-center hover:shadow-sm ${selectedL1 === lang.code
                                    ? 'border-indigo-500 bg-indigo-50 ring-1 ring-indigo-500'
                                    : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                                    }`}
                            >
                                <div className="text-2xl mb-2">{lang.flag}</div>
                                <div className="text-xs font-medium text-gray-700 truncate">{lang.name}</div>
                            </button>
                        ))}
                    </div>
                    <div className="mt-6 flex justify-end">
                        <button
                            onClick={fetchPatterns}
                            disabled={loading}
                            className="px-6 py-2.5 bg-indigo-600 text-white font-medium rounded-lg hover:bg-indigo-700 
                                     transition-colors disabled:opacity-50 disabled:cursor-not-allowed shadow-sm flex items-center gap-2"
                        >
                            {loading ? 'Loading...' : (
                                <>
                                    Load {selectedLang?.name} Transfer Patterns
                                    <ArrowRight className="w-4 h-4" />
                                </>
                            )}
                        </button>
                    </div>
                </div>

                {/* Transfer Patterns Display */}
                {patterns && (
                    <div className="grid md:grid-cols-2 gap-6">
                        {/* Phonology */}
                        <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
                            <div className="border-l-4 border-red-500 p-6 h-full">
                                <h3 className="text-lg font-bold text-gray-900 flex items-center gap-2 mb-6">
                                    <div className="p-2 bg-red-100 rounded-lg">
                                        <AlertTriangle className="w-5 h-5 text-red-600" />
                                    </div>
                                    Phonology Challenges
                                </h3>
                                <div className="space-y-6">
                                    <div>
                                        <p className="text-sm font-semibold text-gray-700 uppercase tracking-wide mb-2">Difficult Sounds</p>
                                        <div className="flex flex-wrap gap-2">
                                            {patterns.phonology.difficult_sounds.map((sound, i) => (
                                                <span key={i} className="px-2.5 py-1 bg-red-50 text-red-700 rounded-md text-sm font-mono border border-red-100">
                                                    {sound}
                                                </span>
                                            ))}
                                        </div>
                                    </div>
                                    <div>
                                        <p className="text-sm font-semibold text-gray-700 uppercase tracking-wide mb-2">Common Substitutions</p>
                                        <ul className="space-y-2">
                                            {Object.entries(patterns.phonology.substitution_patterns).map(([from, to], i) => (
                                                <li key={i} className="text-sm text-gray-600 flex items-center gap-2">
                                                    <span className="font-mono bg-gray-100 px-1.5 py-0.5 rounded text-gray-800">{from}</span>
                                                    <span className="text-gray-400">→</span>
                                                    <span className="font-mono bg-gray-100 px-1.5 py-0.5 rounded text-gray-800">{to}</span>
                                                </li>
                                            ))}
                                        </ul>
                                    </div>
                                    <div>
                                        <p className="text-sm font-semibold text-gray-700 uppercase tracking-wide mb-2">Teaching Strategies</p>
                                        <ul className="space-y-2">
                                            {patterns.phonology.teaching_strategies.map((s, i) => (
                                                <li key={i} className="text-sm text-gray-600 flex items-start gap-2">
                                                    <span className="text-red-500 mt-1">•</span>
                                                    {s}
                                                </li>
                                            ))}
                                        </ul>
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Grammar */}
                        <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
                            <div className="border-l-4 border-orange-500 p-6 h-full">
                                <h3 className="text-lg font-bold text-gray-900 flex items-center gap-2 mb-6">
                                    <div className="p-2 bg-orange-100 rounded-lg">
                                        <BookOpen className="w-5 h-5 text-orange-600" />
                                    </div>
                                    Grammar Challenges
                                </h3>
                                <div className="space-y-6">
                                    <div>
                                        <p className="text-sm font-semibold text-gray-700 uppercase tracking-wide mb-2">Key Challenges</p>
                                        <ul className="space-y-2">
                                            {patterns.grammar.challenges.map((c, i) => (
                                                <li key={i} className="text-sm text-gray-600 flex items-start gap-2">
                                                    <span className="text-orange-500 mt-1">•</span>
                                                    {c}
                                                </li>
                                            ))}
                                        </ul>
                                    </div>
                                    <div>
                                        <p className="text-sm font-semibold text-gray-700 uppercase tracking-wide mb-2">Expected Transfer Errors</p>
                                        <ul className="space-y-2">
                                            {patterns.grammar.transfer_errors.map((e, i) => (
                                                <li key={i} className="text-sm text-gray-600 flex items-start gap-2 bg-orange-50 p-2 rounded-lg border border-orange-100">
                                                    <span className="text-orange-500 mt-0.5">⚠️</span> {e}
                                                </li>
                                            ))}
                                        </ul>
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Vocabulary */}
                        <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
                            <div className="border-l-4 border-green-500 p-6 h-full">
                                <h3 className="text-lg font-bold text-gray-900 flex items-center gap-2 mb-6">
                                    <div className="p-2 bg-green-100 rounded-lg">
                                        <Lightbulb className="w-5 h-5 text-green-600" />
                                    </div>
                                    Vocabulary Insights
                                </h3>
                                <div className="space-y-6">
                                    {patterns.vocabulary.cognates.length > 0 && (
                                        <div>
                                            <p className="text-sm font-semibold text-gray-700 uppercase tracking-wide mb-2">Helpful Cognates</p>
                                            <div className="flex flex-wrap gap-2">
                                                {patterns.vocabulary.cognates.map((c, i) => (
                                                    <span key={i} className="px-2.5 py-1 bg-green-50 text-green-700 rounded-md text-sm border border-green-100">
                                                        {c}
                                                    </span>
                                                ))}
                                            </div>
                                        </div>
                                    )}
                                    {patterns.vocabulary.false_friends.length > 0 && (
                                        <div>
                                            <p className="text-sm font-semibold text-gray-700 uppercase tracking-wide mb-2">False Friends</p>
                                            <div className="flex flex-wrap gap-2">
                                                {patterns.vocabulary.false_friends.map((f, i) => (
                                                    <span key={i} className="px-2.5 py-1 bg-yellow-50 text-yellow-700 rounded-md text-sm border border-yellow-100 flex items-center gap-1">
                                                        <span>⚠️</span> {f}
                                                    </span>
                                                ))}
                                            </div>
                                        </div>
                                    )}
                                </div>
                            </div>
                        </div>

                        {/* Cultural Considerations */}
                        <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
                            <div className="border-l-4 border-purple-500 p-6 h-full">
                                <h3 className="text-lg font-bold text-gray-900 flex items-center gap-2 mb-6">
                                    <div className="p-2 bg-purple-100 rounded-lg">
                                        <Globe className="w-5 h-5 text-purple-600" />
                                    </div>
                                    Cultural Considerations
                                </h3>
                                <ul className="space-y-3">
                                    {patterns.cultural_considerations.map((c, i) => (
                                        <li key={i} className="text-sm text-gray-600 flex items-start gap-3 bg-purple-50 p-3 rounded-lg border border-purple-100">
                                            <span className="text-purple-500 mt-0.5">✦</span> {c}
                                        </li>
                                    ))}
                                </ul>
                            </div>
                        </div>
                    </div>
                )}

                {/* Error Prediction Tool */}
                <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                    <h2 className="text-lg font-bold text-gray-900 mb-4">Error Prediction Tool</h2>
                    <p className="text-sm text-gray-500 mb-4">
                        Enter text a student is about to read or write. We&apos;ll predict likely errors based on L1 transfer patterns.
                    </p>
                    <textarea
                        value={studentText}
                        onChange={(e) => setStudentText(e.target.value)}
                        placeholder="Enter the text the student will encounter..."
                        className="w-full h-32 p-4 border border-gray-300 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none transition-all resize-none"
                    />
                    <div className="flex gap-4 mt-4">
                        <button
                            onClick={predictErrors}
                            disabled={loading || !studentText.trim()}
                            className="px-6 py-2.5 bg-indigo-600 text-white font-medium rounded-lg hover:bg-indigo-700 
                                     transition-colors disabled:opacity-50 disabled:cursor-not-allowed shadow-sm"
                        >
                            Predict Errors
                        </button>
                        <button
                            onClick={generateExercises}
                            disabled={loading}
                            className="px-6 py-2.5 bg-white border border-gray-300 text-gray-700 font-medium rounded-lg 
                                     hover:bg-gray-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed shadow-sm"
                        >
                            Generate Targeted Exercises
                        </button>
                    </div>

                    {predictedErrors.length > 0 && (
                        <div className="mt-6 p-6 bg-yellow-50 border border-yellow-200 rounded-xl">
                            <h4 className="font-bold text-yellow-800 mb-3 flex items-center gap-2">
                                <AlertTriangle className="w-5 h-5" />
                                Predicted Errors for {selectedLang?.name} Speakers
                            </h4>
                            <ul className="space-y-2">
                                {predictedErrors.map((error, i) => (
                                    <li key={i} className="text-sm text-yellow-800 flex items-start gap-2">
                                        <span className="mt-1.5 w-1.5 h-1.5 bg-yellow-500 rounded-full flex-shrink-0" />
                                        {error}
                                    </li>
                                ))}
                            </ul>
                        </div>
                    )}

                    {exercises.length > 0 && (
                        <div className="mt-6 p-6 bg-indigo-50 border border-indigo-200 rounded-xl">
                            <h4 className="font-bold text-indigo-900 mb-4 flex items-center gap-2">
                                <CheckCircle className="w-5 h-5" />
                                Generated Exercises
                            </h4>
                            <div className="grid md:grid-cols-2 gap-4">
                                {exercises.map((ex, i) => (
                                    <div key={i} className="bg-white p-4 rounded-lg border border-indigo-100 shadow-sm">
                                        <div className="flex justify-between items-start mb-2">
                                            <span className="px-2 py-1 bg-indigo-100 text-indigo-700 text-xs font-bold rounded uppercase tracking-wide">
                                                {ex.type}
                                            </span>
                                        </div>
                                        <p className="text-sm text-gray-800 font-medium mb-2">{ex.instruction}</p>
                                        {ex.examples && (
                                            <div className="text-xs text-gray-500 bg-gray-50 p-2 rounded border border-gray-100">
                                                <span className="font-semibold text-gray-700">Examples:</span> {ex.examples.join(', ')}
                                            </div>
                                        )}
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
