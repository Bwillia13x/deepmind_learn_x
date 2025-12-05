"use client";

import { useState } from "react";
import { BarChart3, TrendingUp, Users, AlertTriangle, Search, Filter, Download, Activity, BookOpen, Clock, CheckCircle2 } from "lucide-react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface ClassSummary {
    session_id: number;
    total_assessments: number;
    avg_wpm: number;
    avg_wcpm: number;
    avg_accuracy: number;
    participants_count: number;
}

interface Intervention {
    participant_id: number;
    nickname: string;
    l1: string;
    wpm: number;
    accuracy: number;
    reasons: string[];
    last_assessed: string;
}

interface TrendPoint {
    date: string;
    avg_wpm: number;
    avg_accuracy: number;
    count: number;
}

interface StudentProgress {
    participant_id: number;
    nickname: string;
    assessments: number;
    avg_wpm: number;
    avg_accuracy: number;
    improvement: number;
}

// Simple SVG Line Chart Component
function TrendChart({ data }: { data: TrendPoint[] }) {
    if (data.length === 0) return null;

    const width = 800;
    const height = 300;
    const padding = 40;

    const maxWpm = Math.max(...data.map(d => d.avg_wpm), 100);
    const minWpm = Math.min(...data.map(d => d.avg_wpm), 0);

    const xScale = (i: number) => padding + (i / (data.length - 1 || 1)) * (width - 2 * padding);
    const yScale = (val: number) => height - padding - ((val - minWpm) / (maxWpm - minWpm || 1)) * (height - 2 * padding);

    const wpmPath = data.map((d, i) => `${i === 0 ? 'M' : 'L'} ${xScale(i)} ${yScale(d.avg_wpm)}`).join(' ');
    const accuracyPath = data.map((d, i) => `${i === 0 ? 'M' : 'L'} ${xScale(i)} ${yScale(d.avg_accuracy * 100)}`).join(' ');

    return (
        <div className="w-full overflow-x-auto">
            <svg viewBox={`0 0 ${width} ${height}`} className="w-full h-auto min-w-[600px]">
                {/* Grid lines */}
                {[0, 25, 50, 75, 100].map(v => (
                    <g key={v}>
                        <line
                            x1={padding}
                            y1={yScale(v)}
                            x2={width - padding}
                            y2={yScale(v)}
                            stroke="#e5e7eb"
                            strokeDasharray="4"
                        />
                        <text x={padding - 10} y={yScale(v) + 4} textAnchor="end" className="text-xs fill-gray-400 font-medium">{v}</text>
                    </g>
                ))}

                {/* WPM line */}
                <path d={wpmPath} fill="none" stroke="#6366f1" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" />

                {/* Accuracy line */}
                <path d={accuracyPath} fill="none" stroke="#10b981" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" />

                {/* Data points */}
                {data.map((d, i) => (
                    <g key={i} className="group">
                        <circle cx={xScale(i)} cy={yScale(d.avg_wpm)} r="4" fill="#6366f1" className="transition-all group-hover:r-6" />
                        <circle cx={xScale(i)} cy={yScale(d.avg_accuracy * 100)} r="4" fill="#10b981" className="transition-all group-hover:r-6" />
                        <text
                            x={xScale(i)}
                            y={height - 10}
                            textAnchor="middle"
                            className="text-xs fill-gray-400 font-medium"
                        >
                            {new Date(d.date).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })}
                        </text>
                    </g>
                ))}

                {/* Legend */}
                <g transform={`translate(${width - 200}, 20)`}>
                    <circle cx="0" cy="0" r="4" fill="#6366f1" />
                    <text x="10" y="4" className="text-xs fill-gray-600 font-medium">WPM (Words Per Minute)</text>
                    <circle cx="0" cy="20" r="4" fill="#10b981" />
                    <text x="10" y="24" className="text-xs fill-gray-600 font-medium">Accuracy (%)</text>
                </g>
            </svg>
        </div>
    );
}

// Skeleton component for loading state
function DashboardSkeleton() {
    return (
        <div className="animate-pulse space-y-6">
            <div className="h-8 bg-gray-200 rounded w-1/3"></div>
            <div className="grid grid-cols-1 md:grid-cols-5 gap-6">
                {[1, 2, 3, 4, 5].map((n) => (
                    <div key={n} className="bg-gray-200 rounded-xl h-32"></div>
                ))}
            </div>
            <div className="h-96 bg-gray-200 rounded-xl"></div>
        </div>
    );
}

// Progress Bar Component
function ProgressBar({ value, max, color }: { value: number; max: number; color: string }) {
    const percentage = Math.min((value / max) * 100, 100);
    return (
        <div className="w-full bg-gray-100 rounded-full h-2 overflow-hidden">
            {/* eslint-disable-next-line react/forbid-dom-props */}
            <div
                className={`h-full rounded-full ${color} transition-all duration-500 ease-out`}
                style={{ width: `${percentage}%` }}
            />
        </div>
    );
}

export default function AnalyticsPage() {
    const [sessionId, setSessionId] = useState("1");
    const [summary, setSummary] = useState<ClassSummary | null>(null);
    const [interventions, setInterventions] = useState<Intervention[]>([]);
    const [trends, setTrends] = useState<TrendPoint[]>([]);
    const [studentProgress, setStudentProgress] = useState<StudentProgress[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");
    const [activeTab, setActiveTab] = useState<"overview" | "students" | "trends">("overview");

    const loadAnalytics = async () => {
        if (!sessionId) {
            setError("Please enter a session ID");
            return;
        }

        setLoading(true);
        setError("");

        try {
            // Load summary
            const summaryRes = await fetch(
                `${API_URL}/v1/analytics/class/${sessionId}/summary`
            );
            if (!summaryRes.ok) throw new Error("Failed to load summary");
            const summaryData = await summaryRes.json();
            setSummary(summaryData);

            // Load interventions
            const interventionsRes = await fetch(
                `${API_URL}/v1/analytics/class/${sessionId}/interventions`
            );
            if (!interventionsRes.ok) throw new Error("Failed to load interventions");
            const interventionsData = await interventionsRes.json();
            setInterventions(interventionsData.interventions || []);

            // Load trends
            const trendsRes = await fetch(
                `${API_URL}/v1/analytics/class/${sessionId}/trends?days=30`
            );
            if (!trendsRes.ok) throw new Error("Failed to load trends");
            const trendsData = await trendsRes.json();
            setTrends(trendsData.trend || []);

            // Generate mock student progress data for demo
            const mockProgress: StudentProgress[] = interventionsData.interventions?.map((s: Intervention) => ({
                participant_id: s.participant_id,
                nickname: s.nickname,
                assessments: Math.floor(Math.random() * 10) + 1,
                avg_wpm: s.wpm,
                avg_accuracy: s.accuracy,
                improvement: (Math.random() - 0.3) * 20, // -6% to +14%
            })) || [];
            setStudentProgress(mockProgress);
        } catch (err: any) {
            setError(err.message || "Failed to load analytics");
        } finally {
            setLoading(false);
        }
    };

    const getPerformanceColor = (value: number, type: "wpm" | "accuracy") => {
        if (type === "wpm") {
            if (value >= 80) return "text-green-600";
            if (value >= 60) return "text-yellow-600";
            return "text-red-600";
        } else {
            if (value >= 0.95) return "text-green-600";
            if (value >= 0.85) return "text-yellow-600";
            return "text-red-600";
        }
    };

    return (
        <div className="min-h-screen bg-gray-50 p-8">
            <div className="max-w-7xl mx-auto space-y-8">
                <header>
                    <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
                        <BarChart3 className="w-8 h-8 text-indigo-600" />
                        Analytics Dashboard
                    </h1>
                    <p className="text-gray-500 mt-2 text-lg">
                        Track student progress and identify intervention opportunities
                    </p>
                </header>

                {/* Session Input */}
                <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                    <div className="flex gap-4 items-end max-w-md">
                        <div className="flex-1 space-y-2">
                            <label className="block text-sm font-medium text-gray-700">Session ID</label>
                            <input
                                type="number"
                                placeholder="Enter Session ID"
                                value={sessionId}
                                onChange={(e) => setSessionId(e.target.value)}
                                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-colors"
                            />
                        </div>
                        <button
                            onClick={loadAnalytics}
                            disabled={loading}
                            className="px-6 py-2 bg-indigo-600 text-white font-semibold rounded-lg hover:bg-indigo-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed shadow-sm flex items-center gap-2 h-[42px]"
                        >
                            {loading ? (
                                <>
                                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                                    Loading...
                                </>
                            ) : (
                                <>
                                    <Search className="w-4 h-4" />
                                    Load Analytics
                                </>
                            )}
                        </button>
                    </div>

                    {error && (
                        <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 flex items-center gap-2">
                            <AlertTriangle className="w-5 h-5 flex-shrink-0" />
                            {error}
                        </div>
                    )}
                </div>

                {/* Loading State */}
                {loading && !summary && (
                    <DashboardSkeleton />
                )}

                {summary && (
                    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
                        {/* Tab Navigation */}
                        <div className="border-b border-gray-200">
                            <nav className="flex gap-8" aria-label="Tabs">
                                {[
                                    { id: "overview", label: "Overview", icon: Activity },
                                    { id: "students", label: "Students", icon: Users },
                                    { id: "trends", label: "Trends", icon: TrendingUp },
                                ].map((tab) => (
                                    <button
                                        key={tab.id}
                                        onClick={() => setActiveTab(tab.id as typeof activeTab)}
                                        className={`
                                            py-4 px-1 inline-flex items-center gap-2 border-b-2 font-medium text-sm transition-colors
                                            ${activeTab === tab.id
                                                ? "border-indigo-500 text-indigo-600"
                                                : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
                                            }
                                        `}
                                    >
                                        <tab.icon className="w-4 h-4" />
                                        {tab.label}
                                    </button>
                                ))}
                            </nav>
                        </div>

                        {/* Overview Tab */}
                        {activeTab === "overview" && (
                            <div className="space-y-8">
                                {/* Summary Cards */}
                                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6">
                                    <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                                        <div className="flex items-center justify-between mb-4">
                                            <div className="text-sm font-medium text-gray-500 uppercase tracking-wider">Assessments</div>
                                            <BookOpen className="w-5 h-5 text-indigo-600" />
                                        </div>
                                        <div className="text-3xl font-bold text-gray-900">
                                            {summary.total_assessments}
                                        </div>
                                        <div className="mt-2 text-sm text-gray-500">Total completed</div>
                                    </div>

                                    <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                                        <div className="flex items-center justify-between mb-4">
                                            <div className="text-sm font-medium text-gray-500 uppercase tracking-wider">Avg WPM</div>
                                            <Clock className="w-5 h-5 text-indigo-600" />
                                        </div>
                                        <div className={`text-3xl font-bold mb-2 ${getPerformanceColor(summary.avg_wpm, "wpm")}`}>
                                            {summary.avg_wpm.toFixed(1)}
                                        </div>
                                        <ProgressBar value={summary.avg_wpm} max={150} color="bg-indigo-600" />
                                    </div>

                                    <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                                        <div className="flex items-center justify-between mb-4">
                                            <div className="text-sm font-medium text-gray-500 uppercase tracking-wider">Avg WCPM</div>
                                            <Activity className="w-5 h-5 text-indigo-600" />
                                        </div>
                                        <div className={`text-3xl font-bold mb-2 ${getPerformanceColor(summary.avg_wcpm, "wpm")}`}>
                                            {summary.avg_wcpm.toFixed(1)}
                                        </div>
                                        <ProgressBar value={summary.avg_wcpm} max={150} color="bg-indigo-600" />
                                    </div>

                                    <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                                        <div className="flex items-center justify-between mb-4">
                                            <div className="text-sm font-medium text-gray-500 uppercase tracking-wider">Accuracy</div>
                                            <CheckCircle2 className="w-5 h-5 text-indigo-600" />
                                        </div>
                                        <div className={`text-3xl font-bold mb-2 ${getPerformanceColor(summary.avg_accuracy, "accuracy")}`}>
                                            {(summary.avg_accuracy * 100).toFixed(1)}%
                                        </div>
                                        <ProgressBar value={summary.avg_accuracy * 100} max={100} color="bg-emerald-500" />
                                    </div>

                                    <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                                        <div className="flex items-center justify-between mb-4">
                                            <div className="text-sm font-medium text-gray-500 uppercase tracking-wider">Students</div>
                                            <Users className="w-5 h-5 text-indigo-600" />
                                        </div>
                                        <div className="text-3xl font-bold text-gray-900">
                                            {summary.participants_count}
                                        </div>
                                        <div className="mt-2 text-sm text-gray-500">Active learners</div>
                                    </div>
                                </div>

                                {/* Interventions Needed */}
                                <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
                                    <div className="p-6 border-b border-gray-100 flex justify-between items-center">
                                        <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
                                            <AlertTriangle className="w-5 h-5 text-amber-500" />
                                            Intervention Needed
                                        </h3>
                                        <span className="bg-amber-100 text-amber-800 text-xs font-medium px-2.5 py-0.5 rounded-full">
                                            {interventions.length} Students
                                        </span>
                                    </div>
                                    <div className="divide-y divide-gray-100">
                                        {interventions.length > 0 ? (
                                            interventions.map((student) => (
                                                <div key={student.participant_id} className="p-6 hover:bg-gray-50 transition-colors">
                                                    <div className="flex items-start justify-between">
                                                        <div className="flex items-center gap-4">
                                                            <div className="w-10 h-10 bg-amber-100 rounded-full flex items-center justify-center text-amber-600 font-bold">
                                                                {student.nickname.charAt(0).toUpperCase()}
                                                            </div>
                                                            <div>
                                                                <h4 className="font-semibold text-gray-900">{student.nickname}</h4>
                                                                <p className="text-sm text-gray-500">L1: {student.l1}</p>
                                                            </div>
                                                        </div>
                                                        <div className="text-right">
                                                            <div className="text-sm font-medium text-gray-900">
                                                                Last Assessed: {new Date(student.last_assessed).toLocaleDateString()}
                                                            </div>
                                                            <div className="flex gap-4 mt-1 text-sm">
                                                                <span className={getPerformanceColor(student.wpm, "wpm")}>
                                                                    {student.wpm.toFixed(0)} WPM
                                                                </span>
                                                                <span className={getPerformanceColor(student.accuracy, "accuracy")}>
                                                                    {(student.accuracy * 100).toFixed(0)}% Acc
                                                                </span>
                                                            </div>
                                                        </div>
                                                    </div>
                                                    <div className="mt-4 flex flex-wrap gap-2">
                                                        {student.reasons.map((reason, idx) => (
                                                            <span
                                                                key={idx}
                                                                className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800"
                                                            >
                                                                {reason}
                                                            </span>
                                                        ))}
                                                    </div>
                                                </div>
                                            ))
                                        ) : (
                                            <div className="p-8 text-center text-gray-500">
                                                No interventions needed at this time. Great job!
                                            </div>
                                        )}
                                    </div>
                                </div>
                            </div>
                        )}

                        {/* Students Tab */}
                        {activeTab === "students" && (
                            <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
                                <div className="p-6 border-b border-gray-100 flex justify-between items-center">
                                    <h3 className="text-lg font-semibold text-gray-900">Student Progress</h3>
                                    <div className="flex gap-2">
                                        <button
                                            className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
                                            title="Filter students"
                                            aria-label="Filter students"
                                        >
                                            <Filter className="w-5 h-5" />
                                        </button>
                                        <button
                                            className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
                                            title="Download report"
                                            aria-label="Download report"
                                        >
                                            <Download className="w-5 h-5" />
                                        </button>
                                    </div>
                                </div>
                                <div className="overflow-x-auto">
                                    <table className="w-full text-left text-sm text-gray-600">
                                        <thead className="bg-gray-50 text-xs uppercase font-medium text-gray-500">
                                            <tr>
                                                <th className="px-6 py-4">Student</th>
                                                <th className="px-6 py-4 text-center">Assessments</th>
                                                <th className="px-6 py-4 text-center">Avg WPM</th>
                                                <th className="px-6 py-4 text-center">Avg Accuracy</th>
                                                <th className="px-6 py-4 text-center">Improvement</th>
                                                <th className="px-6 py-4 text-right">Actions</th>
                                            </tr>
                                        </thead>
                                        <tbody className="divide-y divide-gray-100">
                                            {studentProgress.map((student) => (
                                                <tr key={student.participant_id} className="hover:bg-gray-50 transition-colors">
                                                    <td className="px-6 py-4 font-medium text-gray-900">
                                                        {student.nickname}
                                                    </td>
                                                    <td className="px-6 py-4 text-center">
                                                        {student.assessments}
                                                    </td>
                                                    <td className="px-6 py-4 text-center">
                                                        <span className={`font-medium ${getPerformanceColor(student.avg_wpm, "wpm")}`}>
                                                            {student.avg_wpm.toFixed(1)}
                                                        </span>
                                                    </td>
                                                    <td className="px-6 py-4 text-center">
                                                        <span className={`font-medium ${getPerformanceColor(student.avg_accuracy, "accuracy")}`}>
                                                            {(student.avg_accuracy * 100).toFixed(1)}%
                                                        </span>
                                                    </td>
                                                    <td className="px-6 py-4 text-center">
                                                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${student.improvement > 0
                                                                ? "bg-green-100 text-green-800"
                                                                : "bg-red-100 text-red-800"
                                                            }`}>
                                                            {student.improvement > 0 ? "+" : ""}
                                                            {student.improvement.toFixed(1)}%
                                                        </span>
                                                    </td>
                                                    <td className="px-6 py-4 text-right">
                                                        <button className="text-indigo-600 hover:text-indigo-900 font-medium text-sm">
                                                            View Details
                                                        </button>
                                                    </td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        )}

                        {/* Trends Tab */}
                        {activeTab === "trends" && (
                            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                                <div className="flex items-center justify-between mb-6">
                                    <h3 className="text-lg font-semibold text-gray-900">Class Performance Trends (30 Days)</h3>
                                    <select
                                        className="text-sm border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500"
                                        title="Select time range"
                                        aria-label="Select time range"
                                    >
                                        <option>Last 30 Days</option>
                                        <option>Last 90 Days</option>
                                        <option>This Year</option>
                                    </select>
                                </div>
                                <TrendChart data={trends} />
                            </div>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
}
