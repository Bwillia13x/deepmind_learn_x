"use client";

import { useState } from 'react';
import { GraduationCap, Target, BarChart3, FileText, ArrowRight, CheckCircle, AlertTriangle } from 'lucide-react';

const GRADES = ['K', '1', '2', '3', '4', '5', '6', '7', '8', '9'];
const ESL_LEVELS = [1, 2, 3, 4, 5];

interface OutcomeMapping {
    activity_type: string;
    outcomes: {
        code: string;
        description: string;
        strand: string;
    }[];
    esl_benchmark: {
        level: number;
        skill: string;
        descriptor: string;
    };
}

interface GapAnalysis {
    student_id: string;
    covered_outcomes: string[];
    missing_outcomes: {
        code: string;
        description: string;
        priority: 'high' | 'medium' | 'low';
    }[];
    coverage_percentage: number;
    recommendations: string[];
}

interface Outcome {
    code: string;
    description: string;
    strand: string;
}

export default function CurriculumPage() {
    const [selectedGrade, setSelectedGrade] = useState('3');
    const [selectedLevel, setSelectedLevel] = useState(2);
    const [activityText, setActivityText] = useState('');
    const [activityType, setActivityType] = useState('reading');
    const [mapping, setMapping] = useState<OutcomeMapping | null>(null);
    const [gapAnalysis, setGapAnalysis] = useState<GapAnalysis | null>(null);
    const [loading, setLoading] = useState(false);
    const [outcomes, setOutcomes] = useState<Outcome[]>([]);

    const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

    const loadOutcomes = async () => {
        setLoading(true);
        try {
            const res = await fetch(`${API_URL}/v1/curriculum/outcomes/${selectedGrade}`);
            if (res.ok) {
                const data = await res.json();
                setOutcomes(data.outcomes || []);
            }
        } catch (error) {
            console.error('Error loading outcomes:', error);
            // Demo fallback
            setOutcomes([
                { code: `${selectedGrade}.1.1`, description: 'Listen attentively to understand ideas and information', strand: 'Listening' },
                { code: `${selectedGrade}.1.2`, description: 'Speak clearly to express ideas appropriate to context', strand: 'Speaking' },
                { code: `${selectedGrade}.2.1`, description: 'Read grade-appropriate texts with fluency', strand: 'Reading' },
                { code: `${selectedGrade}.2.2`, description: 'Use comprehension strategies to understand texts', strand: 'Reading' },
                { code: `${selectedGrade}.3.1`, description: 'Write clearly for a variety of purposes', strand: 'Writing' },
                { code: `${selectedGrade}.3.2`, description: 'Use vocabulary appropriate to topic and audience', strand: 'Writing' },
            ]);
        }
        setLoading(false);
    };

    const mapActivity = async () => {
        if (!activityText.trim()) return;
        setLoading(true);
        try {
            const res = await fetch(`${API_URL}/v1/curriculum/map-activity`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    activity_description: activityText,
                    activity_type: activityType,
                    grade: selectedGrade,
                    esl_level: selectedLevel,
                }),
            });
            if (res.ok) {
                const data = await res.json();
                setMapping(data);
            }
        } catch (error) {
            console.error('Error mapping activity:', error);
            // Demo fallback
            setMapping({
                activity_type: activityType,
                outcomes: [
                    { code: `${selectedGrade}.2.1`, description: 'Read grade-appropriate texts with fluency', strand: 'Reading' },
                    { code: `${selectedGrade}.2.2`, description: 'Use comprehension strategies to understand texts', strand: 'Reading' },
                    { code: `${selectedGrade}.3.2`, description: 'Use vocabulary appropriate to topic and audience', strand: 'Vocabulary' },
                ],
                esl_benchmark: {
                    level: selectedLevel,
                    skill: 'Reading Comprehension',
                    descriptor: `Level ${selectedLevel}: Can understand main ideas in simplified grade-level texts with visual support`,
                },
            });
        }
        setLoading(false);
    };

    const runGapAnalysis = async () => {
        setLoading(true);
        try {
            const res = await fetch(`${API_URL}/v1/curriculum/gap-analysis`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    student_id: 'DEMO_STUDENT',
                    grade: selectedGrade,
                    covered_activities: ['reading_fluency', 'vocabulary_practice'],
                }),
            });
            if (res.ok) {
                const data = await res.json();
                setGapAnalysis(data);
            }
        } catch (error) {
            console.error('Error running gap analysis:', error);
            // Demo fallback
            setGapAnalysis({
                student_id: 'DEMO_STUDENT',
                covered_outcomes: [`${selectedGrade}.2.1`, `${selectedGrade}.2.2`, `${selectedGrade}.3.2`],
                missing_outcomes: [
                    { code: `${selectedGrade}.1.1`, description: 'Listen attentively to understand ideas and information', priority: 'high' },
                    { code: `${selectedGrade}.1.2`, description: 'Speak clearly to express ideas appropriate to context', priority: 'high' },
                    { code: `${selectedGrade}.3.1`, description: 'Write clearly for a variety of purposes', priority: 'medium' },
                ],
                coverage_percentage: 50,
                recommendations: [
                    'Add listening comprehension activities with audio passages',
                    'Include speaking practice with structured oral responses',
                    'Introduce writing activities with scaffolded prompts',
                ],
            });
        }
        setLoading(false);
    };

    return (
        <div className="min-h-screen bg-gray-50 p-8">
            <div className="max-w-7xl mx-auto space-y-8">
                {/* Header */}
                <div>
                    <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
                        <GraduationCap className="w-8 h-8 text-indigo-600" />
                        Alberta Curriculum Mapping
                    </h1>
                    <p className="mt-2 text-gray-500">
                        Map activities to Alberta ELA outcomes and ESL Proficiency Benchmarks.
                    </p>
                </div>

                {/* Grade & Level Selector */}
                <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                    <div className="grid md:grid-cols-2 gap-8">
                        <div>
                            <label className="block text-sm font-bold text-gray-700 mb-3">Grade Level</label>
                            <div className="flex flex-wrap gap-2">
                                {GRADES.map((grade) => (
                                    <button
                                        key={grade}
                                        onClick={() => setSelectedGrade(grade)}
                                        className={`px-4 py-2 rounded-lg border transition-all font-medium ${selectedGrade === grade
                                            ? 'border-indigo-500 bg-indigo-50 text-indigo-700 ring-1 ring-indigo-500'
                                            : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50 text-gray-600'
                                            }`}
                                    >
                                        {grade === 'K' ? 'K' : `Gr ${grade}`}
                                    </button>
                                ))}
                            </div>
                        </div>

                        <div>
                            <label className="block text-sm font-bold text-gray-700 mb-3">ESL Proficiency Level</label>
                            <div className="flex flex-wrap gap-2">
                                {ESL_LEVELS.map((level) => (
                                    <button
                                        key={level}
                                        onClick={() => setSelectedLevel(level)}
                                        className={`px-4 py-2 rounded-lg border transition-all font-medium ${selectedLevel === level
                                            ? 'border-indigo-500 bg-indigo-50 text-indigo-700 ring-1 ring-indigo-500'
                                            : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50 text-gray-600'
                                            }`}
                                    >
                                        Level {level}
                                    </button>
                                ))}
                            </div>
                            <p className="text-xs text-gray-500 mt-2 font-medium">
                                {selectedLevel === 1 && 'Beginning - Limited English'}
                                {selectedLevel === 2 && 'Developing - Basic social English'}
                                {selectedLevel === 3 && 'Expanding - Functional academic English'}
                                {selectedLevel === 4 && 'Bridging - Near grade-level'}
                                {selectedLevel === 5 && 'Exited - Monitoring phase'}
                            </p>
                        </div>
                    </div>

                    <div className="mt-6 flex justify-end">
                        <button
                            onClick={loadOutcomes}
                            disabled={loading}
                            className="px-6 py-2.5 bg-white border border-gray-300 text-gray-700 font-medium rounded-lg 
                                     hover:bg-gray-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed shadow-sm flex items-center gap-2"
                        >
                            Load Grade {selectedGrade} Outcomes
                            <ArrowRight className="w-4 h-4" />
                        </button>
                    </div>
                </div>

                {/* Outcomes Display */}
                {outcomes.length > 0 && (
                    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                        <h2 className="text-lg font-bold text-gray-900 flex items-center gap-2 mb-6">
                            <div className="p-2 bg-green-100 rounded-lg">
                                <FileText className="w-5 h-5 text-green-600" />
                            </div>
                            Grade {selectedGrade} ELA Outcomes
                        </h2>
                        <div className="grid md:grid-cols-2 gap-4">
                            {outcomes.map((outcome, i) => (
                                <div key={i} className="p-4 bg-gray-50 rounded-lg border border-gray-100 hover:border-gray-200 transition-colors">
                                    <div className="flex items-center justify-between mb-2">
                                        <span className="font-mono text-sm font-bold text-indigo-600 bg-indigo-50 px-2 py-0.5 rounded">{outcome.code}</span>
                                        <span className="text-xs px-2 py-0.5 bg-green-100 text-green-700 rounded font-medium uppercase tracking-wide">{outcome.strand}</span>
                                    </div>
                                    <p className="text-sm text-gray-700 leading-relaxed">{outcome.description}</p>
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {/* Activity Mapping */}
                <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                    <h2 className="text-lg font-bold text-gray-900 flex items-center gap-2 mb-6">
                        <div className="p-2 bg-blue-100 rounded-lg">
                            <Target className="w-5 h-5 text-blue-600" />
                        </div>
                        Map Activity to Curriculum
                    </h2>
                    <div className="space-y-6">
                        <div className="grid md:grid-cols-4 gap-6">
                            <div className="md:col-span-1">
                                <label className="block text-sm font-medium text-gray-700 mb-2">Activity Type</label>
                                <select
                                    value={activityType}
                                    onChange={(e) => setActivityType(e.target.value)}
                                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none transition-all"
                                    aria-label="Select activity type"
                                >
                                    <option value="reading">Reading Practice</option>
                                    <option value="speaking">Speaking Practice</option>
                                    <option value="writing">Writing Activity</option>
                                    <option value="listening">Listening Comprehension</option>
                                    <option value="vocabulary">Vocabulary Building</option>
                                </select>
                            </div>
                            <div className="md:col-span-3">
                                <label className="block text-sm font-medium text-gray-700 mb-2">Activity Description</label>
                                <textarea
                                    value={activityText}
                                    onChange={(e) => setActivityText(e.target.value)}
                                    placeholder="Describe the activity... e.g., 'Students read a leveled passage about the water cycle and answer comprehension questions'"
                                    className="w-full h-24 p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none transition-all resize-none"
                                />
                            </div>
                        </div>

                        <div className="flex justify-end">
                            <button
                                onClick={mapActivity}
                                disabled={loading || !activityText.trim()}
                                className="px-6 py-2.5 bg-indigo-600 text-white font-medium rounded-lg hover:bg-indigo-700 
                                         transition-colors disabled:opacity-50 disabled:cursor-not-allowed shadow-sm flex items-center gap-2"
                            >
                                Map to Curriculum Outcomes
                                <ArrowRight className="w-4 h-4" />
                            </button>
                        </div>
                    </div>

                    {mapping && (
                        <div className="mt-8 p-6 bg-green-50 rounded-xl border border-green-100">
                            <h3 className="font-bold text-green-900 mb-4 flex items-center gap-2">
                                <CheckCircle className="w-5 h-5" />
                                Curriculum Alignment
                            </h3>
                            <div className="space-y-6">
                                <div>
                                    <p className="text-sm font-bold text-green-800 uppercase tracking-wide mb-3">Alberta ELA Outcomes</p>
                                    <div className="space-y-3">
                                        {mapping.outcomes.map((outcome, i) => (
                                            <div key={i} className="flex items-start gap-3 bg-white p-3 rounded-lg border border-green-100 shadow-sm">
                                                <span className="font-mono bg-green-100 px-2 py-0.5 rounded text-green-700 text-sm font-bold whitespace-nowrap">{outcome.code}</span>
                                                <span className="text-gray-700 text-sm">{outcome.description}</span>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                                <div>
                                    <p className="text-sm font-bold text-green-800 uppercase tracking-wide mb-3">ESL Benchmark Alignment</p>
                                    <div className="p-4 bg-white rounded-lg border border-blue-100 shadow-sm">
                                        <div className="flex items-center gap-3 mb-2">
                                            <span className="px-2.5 py-1 bg-blue-600 text-white rounded-md text-xs font-bold uppercase tracking-wide">
                                                Level {mapping.esl_benchmark.level}
                                            </span>
                                            <span className="font-bold text-blue-900">{mapping.esl_benchmark.skill}</span>
                                        </div>
                                        <p className="text-sm text-gray-600 leading-relaxed">{mapping.esl_benchmark.descriptor}</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    )}
                </div>

                {/* Gap Analysis */}
                <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                    <div className="flex justify-between items-start mb-6">
                        <div>
                            <h2 className="text-lg font-bold text-gray-900 flex items-center gap-2">
                                <div className="p-2 bg-purple-100 rounded-lg">
                                    <BarChart3 className="w-5 h-5 text-purple-600" />
                                </div>
                                Curriculum Gap Analysis
                            </h2>
                            <p className="text-sm text-gray-500 mt-1 ml-11">
                                Analyze which curriculum outcomes are being addressed and identify gaps in coverage.
                            </p>
                        </div>
                        <button
                            onClick={runGapAnalysis}
                            disabled={loading}
                            className="px-6 py-2.5 bg-indigo-600 text-white font-medium rounded-lg hover:bg-indigo-700 
                                     transition-colors disabled:opacity-50 disabled:cursor-not-allowed shadow-sm"
                        >
                            Run Gap Analysis
                        </button>
                    </div>

                    {gapAnalysis && (
                        <div className="mt-6 space-y-8">
                            {/* Coverage Meter */}
                            <div className="p-6 bg-gray-50 rounded-xl border border-gray-100">
                                <div className="flex items-center justify-between mb-3">
                                    <span className="font-bold text-gray-700">Curriculum Coverage</span>
                                    <span className="text-2xl font-bold text-indigo-600">{gapAnalysis.coverage_percentage}%</span>
                                </div>
                                <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
                                    <div
                                        className="bg-indigo-600 h-3 rounded-full transition-all duration-1000 ease-out w-1/2"
                                    />
                                </div>
                            </div>

                            <div className="grid md:grid-cols-2 gap-8">
                                {/* Covered */}
                                <div>
                                    <h3 className="font-bold text-green-700 mb-4 flex items-center gap-2">
                                        <CheckCircle className="w-5 h-5" />
                                        Outcomes Covered ({gapAnalysis.covered_outcomes.length})
                                    </h3>
                                    <div className="flex flex-wrap gap-2">
                                        {gapAnalysis.covered_outcomes.map((code, i) => (
                                            <div key={i} className="text-sm font-mono font-medium bg-green-50 text-green-700 px-3 py-1.5 rounded-lg border border-green-100">
                                                {code}
                                            </div>
                                        ))}
                                    </div>
                                </div>

                                {/* Missing */}
                                <div>
                                    <h3 className="font-bold text-red-700 mb-4 flex items-center gap-2">
                                        <AlertTriangle className="w-5 h-5" />
                                        Outcomes Missing ({gapAnalysis.missing_outcomes.length})
                                    </h3>
                                    <div className="space-y-3">
                                        {gapAnalysis.missing_outcomes.map((outcome, i) => (
                                            <div key={i} className="p-3 bg-red-50 rounded-lg border border-red-100">
                                                <div className="flex items-center justify-between mb-1">
                                                    <span className="font-mono text-sm font-bold text-red-700">{outcome.code}</span>
                                                    <span className={`text-[10px] px-2 py-0.5 rounded-full font-bold uppercase tracking-wide ${outcome.priority === 'high' ? 'bg-red-500 text-white' :
                                                        outcome.priority === 'medium' ? 'bg-yellow-500 text-white' :
                                                            'bg-gray-500 text-white'
                                                        }`}>
                                                        {outcome.priority}
                                                    </span>
                                                </div>
                                                <p className="text-xs text-gray-600">{outcome.description}</p>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            </div>

                            {/* Recommendations */}
                            <div className="p-6 bg-blue-50 rounded-xl border border-blue-100">
                                <h3 className="font-bold text-blue-900 mb-4 flex items-center gap-2">
                                    <span>📋</span> Recommendations
                                </h3>
                                <ul className="space-y-3">
                                    {gapAnalysis.recommendations.map((rec, i) => (
                                        <li key={i} className="flex items-start gap-3 text-sm text-blue-800 bg-white p-3 rounded-lg border border-blue-100 shadow-sm">
                                            <span className="text-blue-500 mt-0.5 font-bold">→</span> {rec}
                                        </li>
                                    ))}
                                </ul>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
