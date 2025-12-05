"use client";

import { useState } from "react";
import { Users, School, RefreshCw, XCircle, Copy, CheckCircle2, GraduationCap, UserCircle } from "lucide-react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface Session {
  class_code: string;
  session_id: number;
}

interface Participant {
  id: number;
  nickname: string;
  l1: string;
  joined_at: string | null;
}

export default function SessionPage() {
  const [teacherName, setTeacherName] = useState("");
  const [gradeLevel, setGradeLevel] = useState("");
  const [session, setSession] = useState<Session | null>(null);
  const [classCode, setClassCode] = useState("");
  const [participants, setParticipants] = useState<Participant[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [copied, setCopied] = useState(false);

  const createSession = async () => {
    if (!teacherName.trim() || !gradeLevel.trim()) {
      setError("Please enter teacher name and grade level.");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const response = await fetch(`${API_URL}/auth/create-session`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          teacher_name: teacherName,
          grade_level: gradeLevel,
          settings: {},
        }),
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.statusText}`);
      }

      const data = await response.json();
      setSession(data);
      setClassCode(data.class_code);
    } catch (err: any) {
      setError(err.message || "Failed to create session");
    } finally {
      setLoading(false);
    }
  };

  const loadParticipants = async () => {
    if (!session) return;

    try {
      const response = await fetch(
        `${API_URL}/auth/session/${session.session_id}/participants`
      );

      if (!response.ok) {
        throw new Error(`API error: ${response.statusText}`);
      }

      const data = await response.json();
      setParticipants(data.participants || []);
    } catch (err: any) {
      setError(err.message || "Failed to load participants");
    }
  };

  const closeSession = async () => {
    if (!session) return;

    try {
      const response = await fetch(
        `${API_URL}/auth/session/${session.session_id}/close`,
        { method: "POST" }
      );

      if (!response.ok) {
        throw new Error(`API error: ${response.statusText}`);
      }

      setSession(null);
      setClassCode("");
      setParticipants([]);
    } catch (err: any) {
      setError(err.message || "Failed to close session");
    }
  };

  const copyToClipboard = () => {
    navigator.clipboard.writeText(classCode);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto space-y-8">
        <header>
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
            <School className="w-8 h-8 text-indigo-600" />
            Session Management
          </h1>
          <p className="text-gray-500 mt-2 text-lg">
            Create and manage class sessions for students to join.
          </p>
        </header>

        {!session ? (
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
            <div className="p-6 border-b border-gray-100">
              <h2 className="text-xl font-semibold text-gray-900 flex items-center gap-2">
                <Users className="w-5 h-5 text-indigo-600" />
                Create New Session
              </h2>
            </div>

            <div className="p-6 space-y-6">
              <div className="grid md:grid-cols-2 gap-6">
                <div className="space-y-2">
                  <label className="block text-sm font-medium text-gray-700">
                    Teacher Name
                  </label>
                  <div className="relative">
                    <UserCircle className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                    <input
                      type="text"
                      className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-colors"
                      placeholder="Enter your name"
                      value={teacherName}
                      onChange={(e) => setTeacherName(e.target.value)}
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <label className="block text-sm font-medium text-gray-700">
                    Grade Level
                  </label>
                  <div className="relative">
                    <GraduationCap className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                    <input
                      type="text"
                      className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-colors"
                      placeholder="e.g., Grade 4, ESL Level 2"
                      value={gradeLevel}
                      onChange={(e) => setGradeLevel(e.target.value)}
                    />
                  </div>
                </div>
              </div>

              <button
                onClick={createSession}
                disabled={loading}
                className="w-full bg-indigo-600 text-white font-semibold py-3 rounded-lg hover:bg-indigo-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed shadow-sm flex items-center justify-center gap-2"
              >
                {loading ? (
                  <>
                    <RefreshCw className="w-5 h-5 animate-spin" />
                    Creating...
                  </>
                ) : (
                  <>
                    <CheckCircle2 className="w-5 h-5" />
                    Create Session
                  </>
                )}
              </button>

              {error && (
                <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 flex items-center gap-2">
                  <XCircle className="w-5 h-5 flex-shrink-0" />
                  {error}
                </div>
              )}
            </div>
          </div>
        ) : (
          <div className="space-y-6">
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
              <div className="p-6 border-b border-gray-100 flex justify-between items-center">
                <h2 className="text-xl font-semibold text-gray-900 flex items-center gap-2">
                  <CheckCircle2 className="w-5 h-5 text-green-600" />
                  Active Session
                </h2>
                <div className="flex gap-2">
                  <button
                    onClick={loadParticipants}
                    className="px-4 py-2 bg-white border border-gray-300 text-gray-700 font-medium rounded-lg hover:bg-gray-50 transition-colors flex items-center gap-2"
                  >
                    <RefreshCw className="w-4 h-4" />
                    Refresh
                  </button>
                  <button
                    onClick={closeSession}
                    className="px-4 py-2 bg-red-50 border border-red-200 text-red-700 font-medium rounded-lg hover:bg-red-100 transition-colors flex items-center gap-2"
                  >
                    <XCircle className="w-4 h-4" />
                    Close Session
                  </button>
                </div>
              </div>

              <div className="p-8">
                <div className="bg-indigo-50 rounded-xl p-8 text-center border border-indigo-100">
                  <p className="text-indigo-600 font-medium mb-4">Students can join with this code:</p>
                  <div className="flex justify-center items-center gap-4 mb-6">
                    <div className="text-6xl font-bold text-indigo-700 tracking-widest font-mono">
                      {classCode}
                    </div>
                    <button
                      onClick={copyToClipboard}
                      className="p-2 hover:bg-indigo-100 rounded-full transition-colors text-indigo-500"
                      title="Copy code"
                    >
                      {copied ? <CheckCircle2 className="w-6 h-6" /> : <Copy className="w-6 h-6" />}
                    </button>
                  </div>
                  <div className="flex justify-center gap-8 text-sm text-gray-600">
                    <div className="flex items-center gap-2">
                      <span className="font-semibold">Session ID:</span> {session.session_id}
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="font-semibold">Teacher:</span> {teacherName}
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="font-semibold">Grade:</span> {gradeLevel}
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
              <div className="p-6 border-b border-gray-100">
                <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
                  <Users className="w-5 h-5 text-gray-500" />
                  Participants
                  <span className="bg-gray-100 text-gray-600 px-2 py-0.5 rounded-full text-sm">
                    {participants.length}
                  </span>
                </h3>
              </div>

              {participants.length > 0 ? (
                <div className="divide-y divide-gray-100">
                  {participants.map((p) => (
                    <div
                      key={p.id}
                      className="flex justify-between items-center p-4 hover:bg-gray-50 transition-colors"
                    >
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 bg-indigo-100 rounded-full flex items-center justify-center text-indigo-600 font-semibold">
                          {p.nickname.charAt(0).toUpperCase()}
                        </div>
                        <div>
                          <div className="font-medium text-gray-900">{p.nickname}</div>
                          <div className="text-sm text-gray-500">Native Language: {p.l1}</div>
                        </div>
                      </div>
                      <div className="text-sm text-gray-400">
                        {p.joined_at ? new Date(p.joined_at).toLocaleTimeString() : ""}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="p-12 text-center text-gray-500">
                  <Users className="w-12 h-12 mx-auto text-gray-300 mb-3" />
                  <p>No participants yet.</p>
                  <p className="text-sm mt-1">Students will appear here once they join.</p>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );

