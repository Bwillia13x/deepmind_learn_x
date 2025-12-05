'use client';

import { useState } from 'react';
import { BookOpen, User, Calendar, School, AlertCircle, CheckCircle, ArrowRight, FileText, Target, GraduationCap, Brain } from 'lucide-react';

interface SLIFEAssessment {
    classification: string;
    slife_score: number;
    indicators: string[];
    recommended_level: number;
    level_name: string;
    level_description: string;
    recommended_approaches: string[];
    priority_skills: string[];
}

interface SLIFEPassage {
    id: string;
    title: string;
    topic: string;
    level: number;
    age_range: string;
    content: string;
    vocabulary: string[];
    comprehension_questions: string[];
}

export default function SLIFEPathwaysPage() {
    const [activeTab, setActiveTab] = useState<'assess' | 'passages' | 'resources'>('assess');

    // Assessment form state
    const [age, setAge] = useState<string>('');
    const [grade, setGrade] = useState<string>('');
    const [yearsSchooling, setYearsSchooling] = useState<string>('');
    const [l1Literacy, setL1Literacy] = useState<string>('limited');

    const [assessment, setAssessment] = useState<SLIFEAssessment | null>(null);
    const [passages, setPassages] = useState<SLIFEPassage[]>([]);
    const [selectedLevel, setSelectedLevel] = useState<number>(1);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const handleAssess = async () => {
        if (!age || !grade || !yearsSchooling) {
            setError('Please fill in all required fields');
            return;
        }

        setLoading(true);
        setError(null);

        try {
            const response = await fetch(
                `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/v1/slife/assess`,
                {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        age: parseInt(age),
                        grade,
                        years_schooling: parseInt(yearsSchooling),
                        l1_literacy: l1Literacy
                    })
                }
            );

            if (!response.ok) throw new Error('Assessment failed');

            const data = await response.json();
            setAssessment(data);

            // Auto-fetch passages for recommended level
            if (data.recommended_level) {
                fetchPassages(data.recommended_level);
            }
        } catch (_err) {
            setError('Failed to assess student. Please try again.');
            // Demo data for presentation
            setAssessment({
                classification: 'likely_slife',
                slife_score: 75,
                indicators: [
                    'Schooling gap of 4 years (2+ indicates SLIFE)',
                    'Limited L1 literacy (limited)',
                    'Age-grade mismatch: age 14 in grade 4'
                ],
                recommended_level: 1,
                level_name: 'Emergent',
                level_description: 'Focus on foundational literacy, oral language, and school orientation skills',
                recommended_approaches: [
                    'Use total physical response (TPR) activities',
                    'Incorporate visual supports extensively',
                    'Build on oral language strengths',
                    'Focus on survival/functional vocabulary first'
                ],
                priority_skills: [
                    'Letter recognition and formation',
                    'Basic sight words',
                    'School routines and expectations',
                    'Classroom vocabulary'
                ]
            });
        } finally {
            setLoading(false);
        }
    };

    const fetchPassages = async (level: number) => {
        try {
            const response = await fetch(
                `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/v1/slife/passages?level=${level}`
            );

            if (response.ok) {
                const data = await response.json();
                setPassages(data);
            }
        } catch {
            // Demo passages
            setPassages([
                {
                    id: 'slife-001',
                    title: 'My New School',
                    topic: 'school_orientation',
                    level: 1,
                    age_range: '10-18',
                    content: 'This is my school. It is big. I have a desk. I have a teacher. The teacher helps me. I learn English here.',
                    vocabulary: ['school', 'desk', 'teacher', 'learn', 'English'],
                    comprehension_questions: [
                        'What does the student have?',
                        'Who helps the student?',
                        'What does the student learn?'
                    ]
                },
                {
                    id: 'slife-002',
                    title: 'Going to the Doctor',
                    topic: 'health',
                    level: 1,
                    age_range: '10-18',
                    content: 'I feel sick. My mom takes me to the doctor. The doctor is nice. She checks my ears. She checks my throat. She gives me medicine.',
                    vocabulary: ['sick', 'doctor', 'ears', 'throat', 'medicine'],
                    comprehension_questions: [
                        'How does the student feel?',
                        'Who checks the student?',
                        'What does the doctor check?'
                    ]
                },
                {
                    id: 'slife-003',
                    title: 'Getting a Library Card',
                    topic: 'daily_life',
                    level: 1,
                    age_range: '10-18',
                    content: 'The library has many books. I can borrow books for free. I need a library card. The librarian helps me. Now I can read books at home.',
                    vocabulary: ['library', 'books', 'borrow', 'free', 'card'],
                    comprehension_questions: [
                        'What does the library have?',
                        'What do you need to borrow books?',
                        'Who helps at the library?'
                    ]
                }
            ]);
        }
    };

    const getClassificationColor = (classification: string) => {
        switch (classification) {
            case 'likely_slife': return 'text-red-700 bg-red-50 border-red-200';
            case 'possible_slife': return 'text-amber-700 bg-amber-50 border-amber-200';
            default: return 'text-green-700 bg-green-50 border-green-200';
        }
    };

    const getClassificationLabel = (classification: string) => {
        switch (classification) {
            case 'likely_slife': return 'Likely SLIFE';
            case 'possible_slife': return 'Possibly SLIFE';
            default: return 'Not SLIFE';
        }
    };

    return (
        <div className="min-h-screen bg-gray-50 p-8">
            <div className="max-w-7xl mx-auto space-y-8">
                {/* Header */}
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                    <div>
                        <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
                            <GraduationCap className="w-8 h-8 text-purple-600" />
                            SLIFE Pathways Navigator
                        </h1>
                        <p className="mt-2 text-gray-500">
                            Support for Students with Limited or Interrupted Formal Education
                        </p>
                    </div>
                    <div className="bg-purple-100 text-purple-700 px-4 py-2 rounded-full text-sm font-bold border border-purple-200 shadow-sm">
                        Alberta-Specific
                    </div>
                </div>

                {/* Info Banner */}
                <div className="bg-white border border-purple-100 rounded-xl p-6 shadow-sm relative overflow-hidden">
                    <div className="absolute top-0 right-0 w-32 h-32 bg-purple-50 rounded-full -mr-16 -mt-16 opacity-50"></div>
                    <div className="flex items-start gap-4 relative z-10">
                        <div className="p-3 bg-purple-50 rounded-lg">
                            <AlertCircle className="w-6 h-6 text-purple-600" />
                        </div>
                        <div>
                            <h3 className="text-lg font-bold text-gray-900 mb-2">About SLIFE Students</h3>
                            <p className="text-gray-600 leading-relaxed max-w-4xl">
                                SLIFE students have experienced gaps in their formal education due to circumstances
                                such as war, refugee camps, or lack of access to schools. They often arrive with
                                strong oral language skills but limited print literacy. This tool helps identify
                                SLIFE students and provides age-appropriate, low-reading-level materials.
                            </p>
                        </div>
                    </div>
                </div>

                {/* Tabs */}
                <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-1.5 flex gap-2 overflow-x-auto">
                    <button
                        onClick={() => setActiveTab('assess')}
                        className={`flex-1 px-4 py-3 rounded-lg font-medium transition-all flex items-center justify-center gap-2 whitespace-nowrap ${activeTab === 'assess'
                            ? 'bg-purple-50 text-purple-700 shadow-sm ring-1 ring-purple-200'
                            : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                            }`}
                    >
                        <User className="w-4 h-4" />
                        Assess Student
                    </button>
                    <button
                        onClick={() => { setActiveTab('passages'); fetchPassages(selectedLevel); }}
                        className={`flex-1 px-4 py-3 rounded-lg font-medium transition-all flex items-center justify-center gap-2 whitespace-nowrap ${activeTab === 'passages'
                            ? 'bg-purple-50 text-purple-700 shadow-sm ring-1 ring-purple-200'
                            : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                            }`}
                    >
                        <BookOpen className="w-4 h-4" />
                        Content Library
                    </button>
                    <button
                        onClick={() => setActiveTab('resources')}
                        className={`flex-1 px-4 py-3 rounded-lg font-medium transition-all flex items-center justify-center gap-2 whitespace-nowrap ${activeTab === 'resources'
                            ? 'bg-purple-50 text-purple-700 shadow-sm ring-1 ring-purple-200'
                            : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                            }`}
                    >
                        <Target className="w-4 h-4" />
                        Teaching Resources
                    </button>
                </div>

                {/* Assessment Tab */}
                {activeTab === 'assess' && (
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                        {/* Assessment Form */}
                        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 h-fit">
                            <h2 className="text-xl font-bold text-gray-900 mb-6 flex items-center gap-2">
                                <div className="p-2 bg-purple-100 rounded-lg">
                                    <User className="w-5 h-5 text-purple-600" />
                                </div>
                                Student Assessment
                            </h2>

                            {error && (
                                <div className="mb-6 p-4 bg-amber-50 border border-amber-200 rounded-lg text-amber-800 text-sm flex items-center gap-2">
                                    <AlertCircle className="w-4 h-4" />
                                    {error} (Using demo data)
                                </div>
                            )}

                            <div className="space-y-6">
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                    <div>
                                        <label className="block text-sm font-bold text-gray-700 mb-2">
                                            Age <span className="text-red-500">*</span>
                                        </label>
                                        <input
                                            type="number"
                                            value={age}
                                            onChange={(e) => setAge(e.target.value)}
                                            placeholder="e.g., 14"
                                            min="5"
                                            max="21"
                                            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 outline-none transition-all"
                                        />
                                    </div>
                                    <div>
                                        <label className="block text-sm font-bold text-gray-700 mb-2">
                                            Current Grade <span className="text-red-500">*</span>
                                        </label>
                                        <select
                                            value={grade}
                                            onChange={(e) => setGrade(e.target.value)}
                                            title="Select current grade level"
                                            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 outline-none transition-all bg-white"
                                        >
                                            <option value="">Select grade</option>
                                            <option value="K">Kindergarten</option>
                                            {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12].map(g => (
                                                <option key={g} value={g.toString()}>Grade {g}</option>
                                            ))}
                                        </select>
                                    </div>
                                </div>

                                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                    <div>
                                        <label className="block text-sm font-bold text-gray-700 mb-2 flex items-center gap-2">
                                            <Calendar className="w-4 h-4 text-gray-400" />
                                            Years of Schooling <span className="text-red-500">*</span>
                                        </label>
                                        <input
                                            type="number"
                                            value={yearsSchooling}
                                            onChange={(e) => setYearsSchooling(e.target.value)}
                                            placeholder="e.g., 2"
                                            min="0"
                                            max="15"
                                            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 outline-none transition-all"
                                        />
                                    </div>
                                    <div>
                                        <label className="block text-sm font-bold text-gray-700 mb-2 flex items-center gap-2">
                                            <School className="w-4 h-4 text-gray-400" />
                                            L1 Literacy Level
                                        </label>
                                        <select
                                            value={l1Literacy}
                                            onChange={(e) => setL1Literacy(e.target.value)}
                                            title="Select L1 literacy level"
                                            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 outline-none transition-all bg-white"
                                        >
                                            <option value="none">None (pre-literate)</option>
                                            <option value="limited">Limited</option>
                                            <option value="functional">Functional</option>
                                            <option value="strong">Strong</option>
                                        </select>
                                    </div>
                                </div>

                                <button
                                    onClick={handleAssess}
                                    disabled={loading}
                                    className="w-full px-6 py-3 bg-purple-600 text-white font-bold rounded-lg hover:bg-purple-700 
                                             transition-colors disabled:opacity-50 disabled:cursor-not-allowed shadow-sm flex items-center justify-center gap-2"
                                >
                                    {loading ? 'Assessing...' : 'Assess Student'}
                                    <ArrowRight className="w-5 h-5" />
                                </button>
                            </div>
                        </div>

                        {/* Assessment Results */}
                        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 h-fit">
                            <h2 className="text-xl font-bold text-gray-900 mb-6 flex items-center gap-2">
                                <div className="p-2 bg-blue-100 rounded-lg">
                                    <Brain className="w-5 h-5 text-blue-600" />
                                </div>
                                Assessment Results
                            </h2>

                            {!assessment ? (
                                <div className="text-center py-16 bg-gray-50 rounded-xl border border-dashed border-gray-200">
                                    <User className="w-16 h-16 mx-auto mb-4 text-gray-300" />
                                    <p className="text-gray-500 font-medium">Enter student information to see assessment</p>
                                </div>
                            ) : (
                                <div className="space-y-6">
                                    {/* Classification Badge */}
                                    <div className={`p-5 rounded-xl border ${getClassificationColor(assessment.classification)}`}>
                                        <div className="flex items-center justify-between">
                                            <span className="font-bold text-lg flex items-center gap-2">
                                                <AlertCircle className="w-5 h-5" />
                                                {getClassificationLabel(assessment.classification)}
                                            </span>
                                            <span className="text-sm font-bold bg-white/50 px-3 py-1 rounded-full">
                                                Score: {assessment.slife_score}/100
                                            </span>
                                        </div>
                                    </div>

                                    {/* Indicators */}
                                    <div>
                                        <h4 className="font-bold text-gray-900 mb-3">Key Indicators</h4>
                                        <ul className="space-y-2">
                                            {assessment.indicators.map((indicator, i) => (
                                                <li key={i} className="flex items-start gap-3 text-sm bg-gray-50 p-3 rounded-lg border border-gray-100">
                                                    <AlertCircle className="w-4 h-4 text-amber-500 mt-0.5 flex-shrink-0" />
                                                    <span className="text-gray-700">{indicator}</span>
                                                </li>
                                            ))}
                                        </ul>
                                    </div>

                                    {/* Recommended Level */}
                                    <div className="bg-indigo-50 p-5 rounded-xl border border-indigo-100">
                                        <h4 className="font-bold text-indigo-900 mb-2 flex items-center gap-2">
                                            <BookOpen className="w-4 h-4" />
                                            Recommended Reading Level: {assessment.recommended_level}
                                        </h4>
                                        <p className="text-sm text-indigo-800 font-bold mb-1">{assessment.level_name}</p>
                                        <p className="text-sm text-indigo-700 leading-relaxed">{assessment.level_description}</p>
                                    </div>

                                    {/* Priority Skills */}
                                    <div>
                                        <h4 className="font-bold text-gray-900 mb-3">Priority Skills to Develop</h4>
                                        <div className="flex flex-wrap gap-2">
                                            {assessment.priority_skills.map((skill, i) => (
                                                <span key={i} className="px-3 py-1.5 bg-purple-50 text-purple-700 border border-purple-100 rounded-lg text-xs font-bold">
                                                    {skill}
                                                </span>
                                            ))}
                                        </div>
                                    </div>

                                    {/* Teaching Approaches */}
                                    <div>
                                        <h4 className="font-bold text-gray-900 mb-3">Recommended Approaches</h4>
                                        <ul className="space-y-2">
                                            {assessment.recommended_approaches.map((approach, i) => (
                                                <li key={i} className="flex items-start gap-3 text-sm text-gray-600">
                                                    <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                                                    {approach}
                                                </li>
                                            ))}
                                        </ul>
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>
                )}

                {/* Passages Tab */}
                {activeTab === 'passages' && (
                    <div className="space-y-6">
                        {/* Level Selector */}
                        <div className="flex gap-3 bg-white p-2 rounded-xl shadow-sm border border-gray-200 w-fit">
                            {[1, 2, 3].map(level => (
                                <button
                                    key={level}
                                    onClick={() => { setSelectedLevel(level); fetchPassages(level); }}
                                    className={`px-6 py-2.5 rounded-lg font-bold transition-all ${selectedLevel === level
                                        ? 'bg-purple-600 text-white shadow-sm'
                                        : 'bg-transparent text-gray-600 hover:bg-gray-50'
                                        }`}
                                >
                                    Level {level}: {level === 1 ? 'Emergent' : level === 2 ? 'Early' : 'Transitional'}
                                </button>
                            ))}
                        </div>

                        {/* Passages Grid */}
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                            {passages.map(passage => (
                                <div key={passage.id} className="bg-white rounded-xl shadow-sm border border-gray-200 hover:shadow-md hover:border-purple-200 transition-all group flex flex-col">
                                    <div className="p-6 flex-1">
                                        <div className="flex items-center gap-3 mb-4">
                                            <div className="p-2 bg-purple-50 rounded-lg group-hover:bg-purple-100 transition-colors">
                                                <FileText className="w-5 h-5 text-purple-600" />
                                            </div>
                                            <h3 className="font-bold text-gray-900 text-lg">{passage.title}</h3>
                                        </div>

                                        <div className="flex flex-wrap gap-2 mb-4">
                                            <span className="text-xs font-bold bg-purple-50 text-purple-700 px-2.5 py-1 rounded-md border border-purple-100">
                                                Level {passage.level}
                                            </span>
                                            <span className="text-xs font-bold bg-gray-100 text-gray-600 px-2.5 py-1 rounded-md border border-gray-200">
                                                Ages {passage.age_range}
                                            </span>
                                            <span className="text-xs font-bold bg-blue-50 text-blue-600 px-2.5 py-1 rounded-md border border-blue-100 capitalize">
                                                {passage.topic.replace('_', ' ')}
                                            </span>
                                        </div>

                                        <p className="text-sm text-gray-600 mb-6 leading-relaxed line-clamp-4">
                                            {passage.content}
                                        </p>
                                    </div>

                                    <div className="px-6 py-4 bg-gray-50 border-t border-gray-100 rounded-b-xl">
                                        <p className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">Key Vocabulary</p>
                                        <div className="flex flex-wrap gap-1.5">
                                            {passage.vocabulary.slice(0, 5).map((word, i) => (
                                                <span key={i} className="text-xs bg-white text-gray-700 px-2 py-1 rounded border border-gray-200 shadow-sm">
                                                    {word}
                                                </span>
                                            ))}
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {/* Resources Tab */}
                {activeTab === 'resources' && (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                            <h3 className="font-bold text-xl mb-6 flex items-center gap-3 text-gray-900">
                                <div className="p-2 bg-purple-100 rounded-lg">
                                    <Target className="w-5 h-5 text-purple-600" />
                                </div>
                                Scaffolding Strategies
                            </h3>
                            <ul className="space-y-4">
                                {[
                                    { title: 'Total Physical Response (TPR)', desc: 'Connect vocabulary to physical movements' },
                                    { title: 'Visual Supports', desc: 'Use pictures, diagrams, and realia extensively' },
                                    { title: 'Language Experience Approach', desc: 'Build reading from student-generated oral language' },
                                    { title: 'Cooperative Learning', desc: 'Pair SLIFE students with bilingual peers' },
                                    { title: 'Culturally Relevant Content', desc: 'Connect learning to student backgrounds and experiences' }
                                ].map((strategy, i) => (
                                    <li key={i} className="flex items-start gap-4 p-4 bg-gray-50 rounded-xl border border-gray-100">
                                        <div className="mt-1">
                                            <CheckCircle className="w-5 h-5 text-green-500" />
                                        </div>
                                        <div>
                                            <span className="font-bold text-gray-900 block mb-1">{strategy.title}</span>
                                            <p className="text-sm text-gray-600 leading-relaxed">{strategy.desc}</p>
                                        </div>
                                    </li>
                                ))}
                            </ul>
                        </div>

                        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 h-fit">
                            <h3 className="font-bold text-xl mb-6 flex items-center gap-3 text-gray-900">
                                <div className="p-2 bg-blue-100 rounded-lg">
                                    <School className="w-5 h-5 text-blue-600" />
                                </div>
                                School Readiness Skills
                            </h3>
                            <p className="text-sm text-gray-600 mb-6 bg-blue-50 p-4 rounded-lg border border-blue-100 text-blue-800">
                                SLIFE students may need explicit instruction in these areas to succeed in the classroom environment:
                            </p>
                            <ul className="space-y-3">
                                {[
                                    'Understanding bell schedules and class changes',
                                    'Using lockers and combination locks',
                                    'Navigating cafeteria procedures',
                                    'Asking for help appropriately',
                                    'Understanding homework expectations',
                                    'Using school technology (computers, tablets)',
                                    'Following classroom routines',
                                    'Working in groups and pairs'
                                ].map((skill, i) => (
                                    <li key={i} className="flex items-center gap-3 text-sm text-gray-700 p-3 hover:bg-gray-50 rounded-lg transition-colors">
                                        <div className="w-6 h-6 rounded-full bg-purple-100 flex items-center justify-center flex-shrink-0">
                                            <ArrowRight className="w-3 h-3 text-purple-600" />
                                        </div>
                                        {skill}
                                    </li>
                                ))}
                            </ul>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
