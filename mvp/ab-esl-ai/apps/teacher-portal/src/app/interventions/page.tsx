'use client';

import { useState } from 'react';
import { AlertTriangle, TrendingUp, Target, Calendar, CheckCircle, ArrowRight, Sparkles, FileText } from 'lucide-react';

interface StudentData {
    student_id: string;
    name: string;
    l1_code: string;
    grade: string;
    days_in_canada: number;
    prior_schooling_years: number;
    current_esl_level: number;
    reading_wpm: number;
    reading_accuracy: number;
    vocabulary_score: number;
    sessions_last_30_days: number;
}

interface RiskAssessment {
    student_id: string;
    risk_level: 'low' | 'medium' | 'high' | 'critical';
    risk_score: number;
    warning_indicators: string[];
    skill_gaps: string[];
    recommended_focus: string[];
    weeks_to_benchmark: number;
}

interface InterventionPlan {
    student_id: string;
    plan_duration_weeks: number;
    weekly_schedule: {
        week: number;
        focus_area: string;
        activities: string[];
        target_outcome: string;
        alberta_benchmark: string;
    }[];
    progress_checkpoints: string[];
    success_criteria: string[];
}

const SAMPLE_STUDENTS: StudentData[] = [
    {
        student_id: 'STU001',
        name: 'Ahmed M.',
        l1_code: 'ar',
        grade: '4',
        days_in_canada: 180,
        prior_schooling_years: 3,
        current_esl_level: 2,
        reading_wpm: 45,
        reading_accuracy: 78,
        vocabulary_score: 62,
        sessions_last_30_days: 12,
    },
    {
        student_id: 'STU002',
        name: 'Maria S.',
        l1_code: 'es',
        grade: '3',
        days_in_canada: 365,
        prior_schooling_years: 2,
        current_esl_level: 3,
        reading_wpm: 72,
        reading_accuracy: 88,
        vocabulary_score: 75,
        sessions_last_30_days: 18,
    },
    {
        student_id: 'STU003',
        name: 'Wei L.',
        l1_code: 'zh',
        grade: '5',
        days_in_canada: 90,
        prior_schooling_years: 5,
        current_esl_level: 1,
        reading_wpm: 28,
        reading_accuracy: 65,
        vocabulary_score: 45,
        sessions_last_30_days: 8,
    },
];

export default function InterventionsPage() {
    const [selectedStudent, setSelectedStudent] = useState<StudentData | null>(null);
    const [riskAssessment, setRiskAssessment] = useState<RiskAssessment | null>(null);
    const [interventionPlan, setInterventionPlan] = useState<InterventionPlan | null>(null);
    const [loading, setLoading] = useState(false);

    const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

    const assessRisk = async (student: StudentData) => {
        setSelectedStudent(student);
        setLoading(true);
        setRiskAssessment(null);
        setInterventionPlan(null);

        try {
            const res = await fetch(`${API_URL}/v1/interventions/assess-risk`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(student),
            });
            if (res.ok) {
                const data = await res.json();
                setRiskAssessment(data);
            }
        } catch (error) {
            console.error('Error assessing risk:', error);
            // Demo fallback
            setRiskAssessment({
                student_id: student.student_id,
                risk_level: student.reading_wpm < 50 ? 'high' : student.reading_wpm < 70 ? 'medium' : 'low',
                risk_score: student.reading_wpm < 50 ? 0.78 : student.reading_wpm < 70 ? 0.45 : 0.2,
                warning_indicators: [
                    student.reading_wpm < 60 ? 'Reading fluency below grade level' : null,
                    student.reading_accuracy < 85 ? 'Accuracy indicates decoding gaps' : null,
                    student.vocabulary_score < 70 ? 'Academic vocabulary limited' : null,
                    student.sessions_last_30_days < 15 ? 'Low engagement frequency' : null,
                ].filter(Boolean) as string[],
                skill_gaps: [
                    'Phonemic awareness - consonant blends',
                    'Sight word automaticity',
                    'Reading comprehension strategies',
                ],
                recommended_focus: ['Fluency building', 'Vocabulary development', 'Comprehension monitoring'],
                weeks_to_benchmark: student.reading_wpm < 50 ? 12 : 6,
            });
        }
        setLoading(false);
    };

    const generatePlan = async () => {
        if (!selectedStudent || !riskAssessment) return;
        setLoading(true);

        try {
            const res = await fetch(`${API_URL}/v1/interventions/generate-plan`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    student_id: selectedStudent.student_id,
                    risk_assessment: riskAssessment,
                    l1_code: selectedStudent.l1_code,
                    grade: selectedStudent.grade,
                }),
            });
            if (res.ok) {
                const data = await res.json();
                setInterventionPlan(data);
            }
        } catch (error) {
            console.error('Error generating plan:', error);
            // Demo fallback
            setInterventionPlan({
                student_id: selectedStudent.student_id,
                plan_duration_weeks: 8,
                weekly_schedule: [
                    {
                        week: 1,
                        focus_area: 'Phonemic Awareness',
                        activities: ['Sound segmentation practice', 'Minimal pairs with L1 contrast', 'Blending drills'],
                        target_outcome: 'Segment 3-4 phoneme words with 80% accuracy',
                        alberta_benchmark: 'ESL Level 2 - Phonological Awareness',
                    },
                    {
                        week: 2,
                        focus_area: 'Decoding Fluency',
                        activities: ['Repeated reading passages', 'Sight word flashcards', 'Decodable text practice'],
                        target_outcome: 'Increase WPM by 5 words',
                        alberta_benchmark: 'ELA 3.1.3 - Read grade-level text fluently',
                    },
                    {
                        week: 3,
                        focus_area: 'Vocabulary Building',
                        activities: ['Academic word wall', 'Context clue practice', 'Word family sorts'],
                        target_outcome: 'Master 15 new academic vocabulary words',
                        alberta_benchmark: 'ELA 3.3.2 - Use context clues',
                    },
                    {
                        week: 4,
                        focus_area: 'Comprehension Strategies',
                        activities: ['Prediction practice', 'Graphic organizers', 'Retelling with visual supports'],
                        target_outcome: 'Accurately retell main idea and 2 details',
                        alberta_benchmark: 'ELA 3.2.1 - Identify main idea',
                    },
                ],
                progress_checkpoints: [
                    'Week 2: Quick phonics assessment',
                    'Week 4: Mid-point fluency check (target: +10 WPM)',
                    'Week 6: Vocabulary quiz (target: 80%)',
                    'Week 8: Full benchmark reassessment',
                ],
                success_criteria: [
                    'Reading fluency increases by 20+ WPM',
                    'Reading accuracy reaches 90%',
                    'Moves from ESL Level 2 to Level 3',
                    'Demonstrates grade-level comprehension strategies',
                ],
            });
        }
        setLoading(false);
    };

    const getRiskColor = (level: string) => {
        switch (level) {
            case 'critical':
                return 'bg-red-100 text-red-800 border-red-200';
            case 'high':
                return 'bg-orange-100 text-orange-800 border-orange-200';
            case 'medium':
                return 'bg-yellow-100 text-yellow-800 border-yellow-200';
            case 'low':
                return 'bg-green-100 text-green-800 border-green-200';
            default:
                return 'bg-gray-100 text-gray-800 border-gray-200';
        }
    };

    return (
        <div className="min-h-screen bg-gray-50 p-8">
            <div className="max-w-7xl mx-auto space-y-8">
                {/* Header */}
                <div>
                    <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
                        <AlertTriangle className="w-8 h-8 text-orange-600" />
                        Predictive Intervention Engine
                    </h1>
                    <p className="mt-2 text-gray-500">
                        Identify at-risk students 4-6 weeks early and generate prescriptive intervention plans
                    </p>
                </div>

                {/* Student Selection */}
                <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                    <h2 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
                        <div className="p-2 bg-indigo-50 rounded-lg">
                            <Target className="w-4 h-4 text-indigo-600" />
                        </div>
                        Select Student for Risk Assessment
                    </h2>
                    <div className="grid md:grid-cols-3 gap-4">
                        {SAMPLE_STUDENTS.map((student) => (
                            <button
                                key={student.student_id}
                                onClick={() => assessRisk(student)}
                                className={`p-4 rounded-xl border-2 text-left transition-all hover:shadow-md ${selectedStudent?.student_id === student.student_id
                                        ? 'border-indigo-500 bg-indigo-50 ring-1 ring-indigo-500'
                                        : 'border-gray-200 hover:border-indigo-200 bg-white'
                                    }`}
                            >
                                <div className="flex justify-between items-start mb-2">
                                    <div className="font-bold text-gray-900">{student.name}</div>
                                    <div className="text-xs font-bold px-2 py-1 bg-gray-100 rounded text-gray-600">
                                        Grade {student.grade}
                                    </div>
                                </div>
                                <div className="text-sm text-gray-500 mb-3">
                                    {student.l1_code.toUpperCase()} • ESL Level {student.current_esl_level}
                                </div>
                                <div className="grid grid-cols-2 gap-2 text-xs bg-white p-2 rounded-lg border border-gray-100">
                                    <div>
                                        <span className="text-gray-400 block mb-0.5">WPM</span>
                                        <span className={`font-bold ${student.reading_wpm < 60 ? 'text-red-600' : 'text-gray-900'}`}>
                                            {student.reading_wpm}
                                        </span>
                                    </div>
                                    <div>
                                        <span className="text-gray-400 block mb-0.5">Accuracy</span>
                                        <span className={`font-bold ${student.reading_accuracy < 85 ? 'text-orange-600' : 'text-gray-900'}`}>
                                            {student.reading_accuracy}%
                                        </span>
                                    </div>
                                </div>
                            </button>
                        ))}
                    </div>
                </div>

                {/* Risk Assessment Results */}
                {riskAssessment && (
                    <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden animate-in fade-in slide-in-from-bottom-4 duration-500">
                        <div className="p-6 border-b border-gray-100 bg-gray-50/50 flex flex-col md:flex-row md:items-center justify-between gap-4">
                            <div>
                                <h2 className="text-xl font-bold text-gray-900 flex items-center gap-2">
                                    <TrendingUp className="w-5 h-5 text-indigo-600" />
                                    Risk Assessment Results
                                </h2>
                                <p className="text-sm text-gray-500 mt-1">
                                    Analysis based on recent performance metrics
                                </p>
                            </div>
                            <span className={`px-4 py-2 rounded-lg text-sm font-bold uppercase tracking-wider border ${getRiskColor(riskAssessment.risk_level)}`}>
                                {riskAssessment.risk_level} RISK
                            </span>
                        </div>

                        <div className="p-6 grid md:grid-cols-2 gap-8">
                            <div className="bg-orange-50 rounded-xl p-6 border border-orange-100">
                                <h3 className="font-bold text-orange-900 mb-4 flex items-center gap-2">
                                    <AlertTriangle className="w-5 h-5 text-orange-600" />
                                    Warning Indicators
                                </h3>
                                <ul className="space-y-3">
                                    {riskAssessment.warning_indicators.map((indicator, i) => (
                                        <li key={i} className="flex items-start gap-3 text-sm bg-white p-3 rounded-lg border border-orange-100 shadow-sm">
                                            <div className="w-1.5 h-1.5 rounded-full bg-orange-500 mt-1.5 flex-shrink-0" />
                                            <span className="text-gray-700 font-medium">{indicator}</span>
                                        </li>
                                    ))}
                                </ul>
                            </div>

                            <div className="bg-blue-50 rounded-xl p-6 border border-blue-100">
                                <h3 className="font-bold text-blue-900 mb-4 flex items-center gap-2">
                                    <Target className="w-5 h-5 text-blue-600" />
                                    Skill Gaps Identified
                                </h3>
                                <ul className="space-y-3">
                                    {riskAssessment.skill_gaps.map((gap, i) => (
                                        <li key={i} className="flex items-start gap-3 text-sm bg-white p-3 rounded-lg border border-blue-100 shadow-sm">
                                            <div className="w-1.5 h-1.5 rounded-full bg-blue-500 mt-1.5 flex-shrink-0" />
                                            <span className="text-gray-700 font-medium">{gap}</span>
                                        </li>
                                    ))}
                                </ul>
                            </div>
                        </div>

                        <div className="p-6 border-t border-gray-100 bg-gray-50 flex justify-end">
                            {!interventionPlan ? (
                                <button
                                    onClick={generatePlan}
                                    disabled={loading}
                                    className="bg-indigo-600 text-white font-bold py-3 px-6 rounded-xl hover:bg-indigo-700 transition-all shadow-sm flex items-center gap-2 disabled:opacity-50"
                                >
                                    {loading ? (
                                        <>
                                            <Sparkles className="w-5 h-5 animate-spin" />
                                            Generating Plan...
                                        </>
                                    ) : (
                                        <>
                                            <Sparkles className="w-5 h-5" />
                                            Generate Intervention Plan
                                        </>
                                    )}
                                </button>
                            ) : (
                                <div className="text-green-600 font-bold flex items-center gap-2 bg-green-50 px-4 py-2 rounded-lg border border-green-200">
                                    <CheckCircle className="w-5 h-5" />
                                    Plan Generated Successfully
                                </div>
                            )}
                        </div>
                    </div>
                )}

                {/* Intervention Plan */}
                {interventionPlan && (
                    <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden animate-in fade-in slide-in-from-bottom-8 duration-700">
                        <div className="p-6 border-b border-gray-100 bg-indigo-50/50">
                            <h2 className="text-xl font-bold text-gray-900 flex items-center gap-2">
                                <FileText className="w-5 h-5 text-indigo-600" />
                                Recommended Intervention Plan
                            </h2>
                            <p className="text-sm text-gray-500 mt-1">
                                {interventionPlan.plan_duration_weeks}-week structured program
                            </p>
                        </div>

                        <div className="p-6">
                            <div className="space-y-6">
                                {interventionPlan.weekly_schedule.map((week, i) => (
                                    <div key={i} className="border border-gray-200 rounded-xl overflow-hidden hover:shadow-md transition-shadow">
                                        <div className="bg-gray-50 p-4 border-b border-gray-200 flex justify-between items-center">
                                            <div className="font-bold text-gray-900 flex items-center gap-2">
                                                <div className="bg-indigo-600 text-white text-xs px-2 py-1 rounded">
                                                    Week {week.week}
                                                </div>
                                                {week.focus_area}
                                            </div>
                                            <div className="text-xs font-medium text-gray-500 bg-white px-2 py-1 rounded border border-gray-200">
                                                {week.alberta_benchmark}
                                            </div>
                                        </div>
                                        <div className="p-4 grid md:grid-cols-2 gap-6">
                                            <div>
                                                <div className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-2">Activities</div>
                                                <ul className="space-y-2">
                                                    {week.activities.map((activity, j) => (
                                                        <li key={j} className="text-sm text-gray-600 flex items-start gap-2">
                                                            <div className="w-1 h-1 rounded-full bg-indigo-400 mt-2 flex-shrink-0" />
                                                            {activity}
                                                        </li>
                                                    ))}
                                                </ul>
                                            </div>
                                            <div>
                                                <div className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-2">Target Outcome</div>
                                                <div className="text-sm font-medium text-indigo-700 bg-indigo-50 p-3 rounded-lg border border-indigo-100">
                                                    {week.target_outcome}
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>

                            <div className="mt-8 grid md:grid-cols-2 gap-6">
                                <div className="bg-green-50 rounded-xl p-6 border border-green-100">
                                    <h3 className="font-bold text-green-900 mb-4 flex items-center gap-2">
                                        <CheckCircle className="w-5 h-5 text-green-600" />
                                        Success Criteria
                                    </h3>
                                    <ul className="space-y-2">
                                        {interventionPlan.success_criteria.map((criteria, i) => (
                                            <li key={i} className="flex items-start gap-2 text-sm text-green-800">
                                                <ArrowRight className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                                                {criteria}
                                            </li>
                                        ))}
                                    </ul>
                                </div>

                                <div className="bg-purple-50 rounded-xl p-6 border border-purple-100">
                                    <h3 className="font-bold text-purple-900 mb-4 flex items-center gap-2">
                                        <Calendar className="w-5 h-5 text-purple-600" />
                                        Progress Checkpoints
                                    </h3>
                                    <ul className="space-y-2">
                                        {interventionPlan.progress_checkpoints.map((checkpoint, i) => (
                                            <li key={i} className="flex items-start gap-2 text-sm text-purple-800">
                                                <div className="w-4 h-4 rounded-full border-2 border-purple-400 flex items-center justify-center mt-0.5 flex-shrink-0">
                                                    <div className="w-2 h-2 rounded-full bg-purple-400" />
                                                </div>
                                                {checkpoint}
                                            </li>
                                        ))}
                                    </ul>
                                </div>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
