"use client";

import { useState, useEffect, useRef } from "react";
import { Mic, Users, Play, Square, RotateCcw, Clock, Target, Award, AlertCircle, Download, CheckCircle, MessageSquare } from 'lucide-react';

interface Student {
    id: number;
    name: string;
    l1: string;
    group: string;
}

interface SpeakingGroup {
    id: string;
    name: string;
    students: Student[];
    activity: string;
    status: 'waiting' | 'active' | 'completed';
    progress: number;
}

interface TurnRecord {
    studentId: number;
    studentName: string;
    timestamp: string;
    duration: number;
    audioSnippetUrl?: string;
    transcription?: string;
    accuracy?: number;
}

interface GroupActivity {
    id: string;
    name: string;
    description: string;
    targetSkill: string;
    duration: number; // minutes
    instructions: string[];
}

const ACTIVITIES: GroupActivity[] = [
    {
        id: 'picture_describe',
        name: 'Picture Description',
        description: 'Students take turns describing images to their group',
        targetSkill: 'Descriptive vocabulary, Present tense',
        duration: 10,
        instructions: [
            'Each student picks an image card',
            'Describe the image to your group (30 seconds)',
            'Group members guess what it is',
            'Rotate to next student',
        ],
    },
    {
        id: 'story_chain',
        name: 'Story Chain',
        description: 'Each student adds a sentence to build a collaborative story',
        targetSkill: 'Narrative sequencing, Past tense',
        duration: 8,
        instructions: [
            'First student starts with "Once upon a time..."',
            'Each student adds one sentence',
            'Use transition words (then, next, after that)',
            'Complete at least 2 rounds',
        ],
    },
    {
        id: 'opinion_share',
        name: 'Opinion Sharing',
        description: 'Students share and justify opinions on simple topics',
        targetSkill: 'Opinion expressions, Reasoning',
        duration: 12,
        instructions: [
            'Read the topic question together',
            'Each student shares their opinion',
            'Use "I think... because..." sentence frame',
            'Ask one follow-up question to classmate',
        ],
    },
    {
        id: 'vocabulary_quiz',
        name: 'Vocabulary Quiz',
        description: 'Students quiz each other on weekly vocabulary',
        targetSkill: 'Vocabulary recall, Definition giving',
        duration: 10,
        instructions: [
            'Each student has 3 vocabulary cards',
            'Read the word, partner gives definition',
            'Switch roles after each word',
            'Help if partner is stuck',
        ],
    },
    {
        id: 'role_play',
        name: 'Mini Role-Play',
        description: 'Students act out everyday scenarios',
        targetSkill: 'Pragmatic language, Social phrases',
        duration: 15,
        instructions: [
            'Read the scenario card together',
            'Assign roles (customer, server, etc.)',
            'Practice the conversation 2 times',
            'Switch roles and repeat',
        ],
    },
];

export default function ClassOralsPage() {
    const [students, setStudents] = useState<Student[]>([]);
    const [groups, setGroups] = useState<SpeakingGroup[]>([]);
    const [selectedActivity, setSelectedActivity] = useState<GroupActivity | null>(null);
    const [sessionActive, setSessionActive] = useState(false);
    const [turnRecords, setTurnRecords] = useState<TurnRecord[]>([]);
    const [groupSize, setGroupSize] = useState(4);
    const [showSetup, setShowSetup] = useState(true);
    const timerRef = useRef<NodeJS.Timeout | null>(null);

    // Simulated class roster - in production, fetch from API
    useEffect(() => {
        const sampleStudents: Student[] = [
            { id: 1, name: 'Ahmad K.', l1: 'ar', group: '' },
            { id: 2, name: 'Maria G.', l1: 'es', group: '' },
            { id: 3, name: 'Tuan N.', l1: 'vi', group: '' },
            { id: 4, name: 'Fatima A.', l1: 'ar', group: '' },
            { id: 5, name: 'Ji-Min P.', l1: 'ko', group: '' },
            { id: 6, name: 'Carlos R.', l1: 'es', group: '' },
            { id: 7, name: 'Yuki T.', l1: 'zh', group: '' },
            { id: 8, name: 'Priya S.', l1: 'hi', group: '' },
            { id: 9, name: 'Omar H.', l1: 'ar', group: '' },
            { id: 10, name: 'Sofia M.', l1: 'es', group: '' },
            { id: 11, name: 'Anh L.', l1: 'vi', group: '' },
            { id: 12, name: 'Hassan B.', l1: 'so', group: '' },
            { id: 13, name: 'Lin W.', l1: 'zh', group: '' },
            { id: 14, name: 'Pablo V.', l1: 'es', group: '' },
            { id: 15, name: 'Mei C.', l1: 'zh', group: '' },
            { id: 16, name: 'Raj P.', l1: 'pa', group: '' },
        ];
        setStudents(sampleStudents);
    }, []);

    const createGroups = () => {
        if (!selectedActivity) return;

        const shuffled = [...students].sort(() => Math.random() - 0.5);
        const newGroups: SpeakingGroup[] = [];
        let groupIndex = 0;

        for (let i = 0; i < shuffled.length; i += groupSize) {
            const groupStudents = shuffled.slice(i, i + groupSize);
            const groupName = `Table ${groupIndex + 1}`;

            groupStudents.forEach(s => s.group = groupName);

            newGroups.push({
                id: `group_${groupIndex}`,
                name: groupName,
                students: groupStudents,
                activity: selectedActivity.id,
                status: 'waiting',
                progress: 0,
            });
            groupIndex++;
        }

        setGroups(newGroups);
        setShowSetup(false);
    };

    const startSession = () => {
        setSessionActive(true);
        setGroups(groups.map(g => ({ ...g, status: 'active' })));

        // Simulate progress updates
        timerRef.current = setInterval(() => {
            setGroups(currentGroups =>
                currentGroups.map(g => {
                    if (g.status === 'active') {
                        const newProgress = Math.min(g.progress + Math.random() * 15, 100);
                        return {
                            ...g,
                            progress: newProgress,
                            status: newProgress >= 100 ? 'completed' : 'active',
                        };
                    }
                    return g;
                })
            );

            // Simulate turn records
            if (Math.random() > 0.7) {
                const randomGroup = groups[Math.floor(Math.random() * groups.length)];
                if (randomGroup && randomGroup.students.length > 0) {
                    const randomStudent = randomGroup.students[Math.floor(Math.random() * randomGroup.students.length)];
                    const newRecord: TurnRecord = {
                        studentId: randomStudent.id,
                        studentName: randomStudent.name,
                        timestamp: new Date().toLocaleTimeString(),
                        duration: 15 + Math.floor(Math.random() * 30),
                        accuracy: 60 + Math.floor(Math.random() * 35),
                        transcription: getRandomTranscription(),
                    };
                    setTurnRecords(prev => [newRecord, ...prev].slice(0, 20));
                }
            }
        }, 3000);
    };

    const stopSession = () => {
        setSessionActive(false);
        if (timerRef.current) {
            clearInterval(timerRef.current);
        }
        setGroups(groups.map(g => ({ ...g, status: 'completed' })));
    };

    const getRandomTranscription = () => {
        const samples = [
            "I see a big red ball in the picture...",
            "Then the boy went to the park and...",
            "I think pizza is better because it has cheese...",
            "The word 'happy' means feeling good...",
            "Hello, I would like to order a sandwich please...",
        ];
        return samples[Math.floor(Math.random() * samples.length)];
    };

    const getGroupStatusColor = (status: string) => {
        switch (status) {
            case 'active': return 'bg-green-50 border-green-200 text-green-800';
            case 'completed': return 'bg-blue-50 border-blue-200 text-blue-800';
            default: return 'bg-gray-50 border-gray-200 text-gray-600';
        }
    };

    const resetSession = () => {
        setGroups([]);
        setTurnRecords([]);
        setSessionActive(false);
        setShowSetup(true);
        setSelectedActivity(null);
    };

    const calculateParticipation = () => {
        const counts: Record<number, number> = {};
        turnRecords.forEach(r => {
            counts[r.studentId] = (counts[r.studentId] || 0) + 1;
        });
        return counts;
    };

    const participation = calculateParticipation();

    return (
        <div className="min-h-screen bg-gray-50 p-8">
            {/* Header */}
            <div className="max-w-7xl mx-auto mb-8">
                <div className="flex justify-between items-center">
                    <div>
                        <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
                            <Mic className="w-8 h-8 text-purple-600" />
                            Class Orals Manager
                        </h1>
                        <p className="text-gray-500 mt-2">
                            AI-monitored small-group speaking activities
                        </p>
                    </div>
                    {!showSetup && (
                        <button
                            onClick={resetSession}
                            className="px-4 py-2 bg-white border border-gray-200 hover:bg-gray-50 rounded-lg text-gray-700 font-medium shadow-sm flex items-center gap-2 transition-colors"
                        >
                            <RotateCcw className="w-4 h-4" />
                            Reset Session
                        </button>
                    )}
                </div>
            </div>

            <div className="max-w-7xl mx-auto">
                {showSetup ? (
                    /* Setup Phase */
                    <div className="space-y-8">
                        {/* Activity Selection */}
                        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                            <h2 className="text-xl font-bold text-gray-900 mb-6 flex items-center gap-2">
                                <div className="p-2 bg-purple-100 rounded-lg">
                                    <MessageSquare className="w-5 h-5 text-purple-600" />
                                </div>
                                1. Select Speaking Activity
                            </h2>
                            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                                {ACTIVITIES.map(activity => (
                                    <button
                                        key={activity.id}
                                        onClick={() => setSelectedActivity(activity)}
                                        className={`p-5 rounded-xl border-2 text-left transition-all hover:shadow-md ${selectedActivity?.id === activity.id
                                            ? 'border-purple-500 bg-purple-50 ring-1 ring-purple-500'
                                            : 'border-gray-100 hover:border-purple-200 bg-gray-50'
                                            }`}
                                    >
                                        <h3 className="font-bold text-gray-900 mb-2">{activity.name}</h3>
                                        <p className="text-sm text-gray-600 mb-4 line-clamp-2">{activity.description}</p>
                                        <div className="flex items-center gap-3 text-xs font-medium text-gray-500">
                                            <span className="flex items-center gap-1 bg-white px-2 py-1 rounded border border-gray-200">
                                                <Clock className="w-3 h-3" /> {activity.duration} min
                                            </span>
                                            <span className="flex items-center gap-1 bg-white px-2 py-1 rounded border border-gray-200">
                                                <Target className="w-3 h-3" /> {activity.targetSkill}
                                            </span>
                                        </div>
                                    </button>
                                ))}
                            </div>
                        </div>

                        {/* Activity Details */}
                        {selectedActivity && (
                            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
                                <h2 className="text-xl font-bold text-gray-900 mb-6 flex items-center gap-2">
                                    <div className="p-2 bg-blue-100 rounded-lg">
                                        <CheckCircle className="w-5 h-5 text-blue-600" />
                                    </div>
                                    {selectedActivity.name} Instructions
                                </h2>
                                <div className="bg-blue-50 rounded-xl p-6 border border-blue-100">
                                    <ol className="list-decimal list-inside space-y-3 text-gray-700">
                                        {selectedActivity.instructions.map((inst, idx) => (
                                            <li key={idx} className="font-medium">{inst}</li>
                                        ))}
                                    </ol>
                                </div>
                            </div>
                        )}

                        {/* Group Configuration */}
                        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                            <h2 className="text-xl font-bold text-gray-900 mb-6 flex items-center gap-2">
                                <div className="p-2 bg-green-100 rounded-lg">
                                    <Users className="w-5 h-5 text-green-600" />
                                </div>
                                2. Configure Groups
                            </h2>
                            <div className="flex flex-col md:flex-row md:items-center gap-6 mb-8">
                                <div className="flex-1">
                                    <label className="block text-sm font-bold text-gray-700 mb-2">Students per group</label>
                                    <select
                                        value={groupSize}
                                        onChange={(e) => setGroupSize(Number(e.target.value))}
                                        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 outline-none bg-white"
                                        title="Select number of students per group"
                                    >
                                        <option value={3}>3 students</option>
                                        <option value={4}>4 students</option>
                                        <option value={5}>5 students</option>
                                    </select>
                                </div>
                                <div className="flex-1 flex items-center">
                                    <div className="bg-gray-50 px-4 py-3 rounded-lg border border-gray-200 text-gray-600 font-medium w-full">
                                        Generating <span className="font-bold text-gray-900">{Math.ceil(students.length / groupSize)}</span> groups from <span className="font-bold text-gray-900">{students.length}</span> students
                                    </div>
                                </div>
                            </div>
                            <button
                                onClick={createGroups}
                                disabled={!selectedActivity}
                                className={`w-full md:w-auto px-8 py-4 rounded-xl font-bold text-lg transition-all shadow-sm flex items-center justify-center gap-2 ${selectedActivity
                                    ? 'bg-purple-600 hover:bg-purple-700 text-white hover:shadow-md'
                                    : 'bg-gray-100 text-gray-400 cursor-not-allowed'
                                    }`}
                            >
                                Create Groups & Continue
                                <Users className="w-5 h-5" />
                            </button>
                        </div>
                    </div>
                ) : (
                    /* Session Phase */
                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                        {/* Groups Panel */}
                        <div className="lg:col-span-2 space-y-6">
                            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
                                    <h2 className="text-xl font-bold text-gray-900 flex items-center gap-2">
                                        <Target className="w-5 h-5 text-purple-600" />
                                        {selectedActivity?.name} - Groups
                                    </h2>
                                    {!sessionActive ? (
                                        <button
                                            onClick={startSession}
                                            className="px-6 py-2.5 bg-green-600 hover:bg-green-700 text-white rounded-lg font-bold shadow-sm flex items-center justify-center gap-2 transition-colors"
                                        >
                                            <Play className="w-4 h-4 fill-current" />
                                            Start All Groups
                                        </button>
                                    ) : (
                                        <button
                                            onClick={stopSession}
                                            className="px-6 py-2.5 bg-red-600 hover:bg-red-700 text-white rounded-lg font-bold shadow-sm flex items-center justify-center gap-2 transition-colors"
                                        >
                                            <Square className="w-4 h-4 fill-current" />
                                            End Session
                                        </button>
                                    )}
                                </div>

                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                    {groups.map(group => (
                                        <div
                                            key={group.id}
                                            className={`p-5 rounded-xl border transition-all ${getGroupStatusColor(group.status)}`}
                                        >
                                            <div className="flex justify-between items-center mb-4">
                                                <h3 className="font-bold text-lg">{group.name}</h3>
                                                <span className={`text-xs font-bold uppercase tracking-wider px-2.5 py-1 rounded-full ${group.status === 'active' ? 'bg-green-100 text-green-700' :
                                                    group.status === 'completed' ? 'bg-blue-100 text-blue-700' :
                                                        'bg-gray-200 text-gray-600'
                                                    }`}>
                                                    {group.status}
                                                </span>
                                            </div>

                                            {/* Students */}
                                            <div className="flex flex-wrap gap-2 mb-4">
                                                {group.students.map(student => {
                                                    const turns = participation[student.id] || 0;
                                                    return (
                                                        <span
                                                            key={student.id}
                                                            className={`px-2.5 py-1 rounded-md text-sm font-medium border transition-colors ${turns > 0
                                                                ? 'bg-white border-green-200 text-green-700 shadow-sm'
                                                                : 'bg-white/50 border-transparent text-gray-500'
                                                                }`}
                                                            title={`${turns} turns`}
                                                        >
                                                            {student.name}
                                                            {turns > 0 && <sup className="ml-1 font-bold text-green-600">{turns}</sup>}
                                                        </span>
                                                    );
                                                })}
                                            </div>

                                            {/* Progress Bar */}
                                            {group.status !== 'waiting' && (
                                                <div className="w-full bg-white/50 rounded-full h-2.5 overflow-hidden">
                                                    {/* eslint-disable-next-line react/forbid-dom-props */}
                                                    <div
                                                        className="bg-green-500 h-full rounded-full transition-all duration-500 ease-out"
                                                        style={{ width: `${group.progress}%` } as React.CSSProperties} // eslint-disable-line
                                                    />
                                                </div>
                                            )}
                                        </div>
                                    ))}
                                </div>
                            </div>

                            {/* Turn Records */}
                            {turnRecords.length > 0 && (
                                <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                                    <h2 className="text-xl font-bold text-gray-900 mb-6 flex items-center gap-2">
                                        <MessageSquare className="w-5 h-5 text-blue-600" />
                                        Live Turn Log
                                    </h2>
                                    <div className="space-y-3 max-h-80 overflow-y-auto pr-2 custom-scrollbar">
                                        {turnRecords.map((record, idx) => (
                                            <div
                                                key={idx}
                                                className="flex flex-col sm:flex-row sm:items-center gap-3 p-3 bg-gray-50 rounded-xl border border-gray-100 hover:border-gray-200 transition-colors"
                                            >
                                                <div className="flex items-center gap-3 min-w-[180px]">
                                                    <span className="text-xs font-medium text-gray-400 bg-white px-2 py-1 rounded border border-gray-200">
                                                        {record.timestamp}
                                                    </span>
                                                    <span className="font-bold text-gray-900">
                                                        {record.studentName}
                                                    </span>
                                                </div>

                                                <div className="flex-1 min-w-0">
                                                    <p className="text-sm text-gray-600 italic truncate">
                                                        &quot;{record.transcription}&quot;
                                                    </p>
                                                </div>

                                                <div className="flex items-center gap-3">
                                                    <span className={`text-sm font-bold px-2 py-0.5 rounded ${(record.accuracy || 0) >= 80 ? 'bg-green-100 text-green-700' :
                                                        (record.accuracy || 0) >= 60 ? 'bg-yellow-100 text-yellow-700' :
                                                            'bg-orange-100 text-orange-700'
                                                        }`}>
                                                        {record.accuracy}%
                                                    </span>
                                                    <span className="text-xs font-medium text-gray-400 bg-white px-2 py-1 rounded border border-gray-200">
                                                        {record.duration}s
                                                    </span>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}
                        </div>

                        {/* Stats Panel */}
                        <div className="space-y-6">
                            {/* Session Stats */}
                            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                                <h2 className="text-lg font-bold text-gray-900 mb-6 flex items-center gap-2">
                                    <div className="p-2 bg-purple-100 rounded-lg">
                                        <Clock className="w-4 h-4 text-purple-600" />
                                    </div>
                                    Session Stats
                                </h2>
                                <div className="space-y-4">
                                    <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                                        <span className="text-gray-600 font-medium">Groups Active</span>
                                        <span className="font-bold text-green-600 bg-white px-2 py-1 rounded border border-gray-200 shadow-sm">
                                            {groups.filter(g => g.status === 'active').length} / {groups.length}
                                        </span>
                                    </div>
                                    <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                                        <span className="text-gray-600 font-medium">Total Turns</span>
                                        <span className="font-bold text-purple-600 bg-white px-2 py-1 rounded border border-gray-200 shadow-sm">
                                            {turnRecords.length}
                                        </span>
                                    </div>
                                    <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                                        <span className="text-gray-600 font-medium">Avg Accuracy</span>
                                        <span className="font-bold text-blue-600 bg-white px-2 py-1 rounded border border-gray-200 shadow-sm">
                                            {turnRecords.length > 0
                                                ? Math.round(
                                                    turnRecords.reduce((sum, r) => sum + (r.accuracy || 0), 0) /
                                                    turnRecords.length
                                                )
                                                : 0}%
                                        </span>
                                    </div>
                                    <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                                        <span className="text-gray-600 font-medium">Participation</span>
                                        <span className="font-bold text-orange-600 bg-white px-2 py-1 rounded border border-gray-200 shadow-sm">
                                            {Object.keys(participation).length} / {students.length}
                                        </span>
                                    </div>
                                </div>
                            </div>

                            {/* Participation Leaderboard */}
                            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                                <h2 className="text-lg font-bold text-gray-900 mb-6 flex items-center gap-2">
                                    <div className="p-2 bg-yellow-100 rounded-lg">
                                        <Award className="w-4 h-4 text-yellow-600" />
                                    </div>
                                    Top Speakers
                                </h2>
                                <div className="space-y-3">
                                    {Object.entries(participation)
                                        .sort((a, b) => b[1] - a[1])
                                        .slice(0, 5)
                                        .map(([studentId, count], idx) => {
                                            const student = students.find(s => s.id === Number(studentId));
                                            return (
                                                <div
                                                    key={studentId}
                                                    className="flex items-center gap-3 p-3 rounded-lg bg-gray-50 border border-gray-100"
                                                >
                                                    <span className="text-xl w-8 text-center">
                                                        {idx === 0 ? '🥇' : idx === 1 ? '🥈' : idx === 2 ? '🥉' : `${idx + 1}`}
                                                    </span>
                                                    <span className="flex-1 font-medium text-gray-900">
                                                        {student?.name || `Student ${studentId}`}
                                                    </span>
                                                    <span className="font-bold text-purple-600 bg-purple-50 px-2 py-0.5 rounded text-sm">
                                                        {count} turns
                                                    </span>
                                                </div>
                                            );
                                        })}
                                </div>
                            </div>

                            {/* Needs Attention */}
                            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                                <h2 className="text-lg font-bold text-gray-900 mb-6 flex items-center gap-2">
                                    <div className="p-2 bg-red-100 rounded-lg">
                                        <AlertCircle className="w-4 h-4 text-red-600" />
                                    </div>
                                    Needs Attention
                                </h2>
                                <div className="space-y-3">
                                    {students
                                        .filter(s => !participation[s.id])
                                        .slice(0, 5)
                                        .map(student => (
                                            <div
                                                key={student.id}
                                                className="flex items-center gap-3 p-3 rounded-lg bg-red-50 border border-red-100"
                                            >
                                                <div className="w-2 h-2 rounded-full bg-red-500"></div>
                                                <span className="font-medium text-gray-900">{student.name}</span>
                                                <span className="text-xs font-bold text-red-600 bg-white px-2 py-1 rounded ml-auto">
                                                    No turns
                                                </span>
                                            </div>
                                        ))}
                                    {students.filter(s => !participation[s.id]).length === 0 && (
                                        <div className="flex flex-col items-center justify-center py-6 text-center">
                                            <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mb-3">
                                                <CheckCircle className="w-6 h-6 text-green-600" />
                                            </div>
                                            <p className="text-green-700 font-bold">
                                                All students have participated!
                                            </p>
                                        </div>
                                    )}
                                </div>
                            </div>

                            {/* Export Button */}
                            {turnRecords.length > 0 && (
                                <button className="w-full px-6 py-4 bg-blue-600 hover:bg-blue-700 text-white rounded-xl font-bold shadow-sm flex items-center justify-center gap-2 transition-colors">
                                    <Download className="w-5 h-5" />
                                    Export Session Report
                                </button>
                            )}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
