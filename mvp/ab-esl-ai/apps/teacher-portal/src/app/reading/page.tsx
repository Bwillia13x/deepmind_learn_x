"use client";

import { useState } from "react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface ReadingResult {
  wpm: number;
  wcpm?: number;
  accuracy?: number;
  passage_id?: string;
  participant_id: number;
  created_at: string;
}

export default function ReadingPage() {
  const [sessionId, setSessionId] = useState("");
  const [results, setResults] = useState<ReadingResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const loadResults = async () => {
    if (!sessionId.trim()) {
      setError("Please enter a session ID.");
      return;
    }

    setLoading(true);
    setError("");
    setResults([]);

    try {
      const response = await fetch(
        `${API_URL}/v1/reading/session/${sessionId}/results`
      );

      if (!response.ok) {
        throw new Error(`API error: ${response.statusText}`);
      }

      const data = await response.json();
      setResults(data.results || []);
    } catch (err: any) {
      setError(err.message || "Failed to load reading results");
    } finally {
      setLoading(false);
    }
  };

  const downloadCSV = () => {
    if (results.length === 0) return;

    const headers = ["Participant ID", "WPM", "WCPM", "Accuracy", "Passage ID", "Date"];
    const rows = results.map((r) => [
      r.participant_id,
      r.wpm.toFixed(1),
      r.wcpm?.toFixed(1) || "N/A",
      r.accuracy ? (r.accuracy * 100).toFixed(1) + "%" : "N/A",
      r.passage_id || "N/A",
      new Date(r.created_at).toLocaleString(),
    ]);

    const csvContent =
      [headers.join(","), ...rows.map((row) => row.join(","))].join("\n");

    const blob = new Blob([csvContent], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `reading-results-session-${sessionId}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const getPerformanceColor = (accuracy?: number) => {
    if (!accuracy) return "text-gray-600";
    if (accuracy >= 0.95) return "text-green-600 bg-green-50 border-green-200";
    if (accuracy >= 0.85) return "text-yellow-600 bg-yellow-50 border-yellow-200";
    return "text-red-600 bg-red-50 border-red-200";
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Reading Results Dashboard</h1>
          <p className="text-gray-500 mt-2">
            View reading scores and performance metrics for your class.
          </p>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-8">
          <label className="block text-sm font-medium text-gray-700 mb-2">Session ID</label>
          <div className="flex gap-4 max-w-md">
            <input
              type="number"
              className="flex-1 border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none transition-all"
              placeholder="Enter session ID"
              value={sessionId}
              onChange={(e) => setSessionId(e.target.value)}
            />
            <button
              onClick={loadResults}
              disabled={loading}
              className="px-6 py-2 bg-indigo-600 text-white font-medium rounded-lg hover:bg-indigo-700 
                       transition-colors disabled:opacity-50 disabled:cursor-not-allowed shadow-sm"
            >
              {loading ? "Loading..." : "Load Results"}
            </button>
          </div>

          {error && (
            <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
              {error}
            </div>
          )}
        </div>

        {results.length > 0 && (
          <div className="space-y-8">
            {/* Summary Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                <div className="text-sm font-medium text-gray-500 mb-1">Avg WPM</div>
                <div className="text-3xl font-bold text-indigo-600">
                  {(results.reduce((sum, r) => sum + r.wpm, 0) / results.length).toFixed(1)}
                </div>
              </div>

              {results.some((r) => r.wcpm) && (
                <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                  <div className="text-sm font-medium text-gray-500 mb-1">Avg WCPM</div>
                  <div className="text-3xl font-bold text-pink-600">
                    {(
                      results
                        .filter((r) => r.wcpm)
                        .reduce((sum, r) => sum + (r.wcpm || 0), 0) /
                      results.filter((r) => r.wcpm).length
                    ).toFixed(1)}
                  </div>
                </div>
              )}

              {results.some((r) => r.accuracy) && (
                <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                  <div className="text-sm font-medium text-gray-500 mb-1">Avg Accuracy</div>
                  <div className="text-3xl font-bold text-green-600">
                    {(
                      (results
                        .filter((r) => r.accuracy)
                        .reduce((sum, r) => sum + (r.accuracy || 0), 0) /
                        results.filter((r) => r.accuracy).length) *
                      100
                    ).toFixed(0)}%
                  </div>
                </div>
              )}

              <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                <div className="text-sm font-medium text-gray-500 mb-1">Total Readings</div>
                <div className="text-3xl font-bold text-gray-900">{results.length}</div>
              </div>
            </div>

            {/* Results Grid */}
            <div>
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-xl font-bold text-gray-900">
                  Detailed Results
                </h2>
                <button
                  onClick={downloadCSV}
                  className="px-4 py-2 bg-white border border-gray-300 text-gray-700 font-medium rounded-lg 
                           hover:bg-gray-50 transition-colors shadow-sm flex items-center gap-2"
                >
                  <span>📥</span> Download CSV
                </button>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {results.map((result, idx) => (
                  <div key={idx} className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow">
                    <div className="flex justify-between items-start mb-4">
                      <div>
                        <h3 className="text-lg font-bold text-gray-900">
                          Participant {result.participant_id}
                        </h3>
                        <p className="text-xs text-gray-500 mt-1">
                          {new Date(result.created_at).toLocaleString()}
                        </p>
                      </div>
                      {result.accuracy && (
                        <span
                          className={`px-3 py-1 rounded-full text-sm font-bold border ${getPerformanceColor(result.accuracy)}`}
                        >
                          {(result.accuracy * 100).toFixed(0)}%
                        </span>
                      )}
                    </div>

                    <div className="space-y-3">
                      <div className="flex justify-between items-center p-2 bg-gray-50 rounded-lg">
                        <span className="text-sm text-gray-600">WPM</span>
                        <span className="font-bold text-gray-900">
                          {result.wpm.toFixed(1)}
                        </span>
                      </div>

                      {result.wcpm && (
                        <div className="flex justify-between items-center p-2 bg-gray-50 rounded-lg">
                          <span className="text-sm text-gray-600">WCPM</span>
                          <span className="font-bold text-gray-900">
                            {result.wcpm.toFixed(1)}
                          </span>
                        </div>
                      )}

                      {result.passage_id && (
                        <div className="flex justify-between items-center p-2 bg-gray-50 rounded-lg">
                          <span className="text-sm text-gray-600">Passage</span>
                          <span className="text-sm font-medium text-gray-900 truncate max-w-[150px]" title={result.passage_id}>
                            {result.passage_id}
                          </span>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {results.length === 0 && sessionId && !loading && !error && (
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-12 text-center">
            <div className="text-4xl mb-4">📊</div>
            <h3 className="text-lg font-medium text-gray-900">No results found</h3>
            <p className="text-gray-500 mt-1">
              No reading results found for session ID {sessionId}.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
