"use client";

import { useState } from 'react';
import { Loader2, Copy, RefreshCw, BookOpen, Check, Trash2, Plus } from 'lucide-react';

const SCOPE_SEQUENCE = {
  'Unit 1': ['m', 's', 'a', 't'],
  'Unit 2': ['p', 'n', 'i'],
  'Unit 3': ['c', 'd', 'o'],
  'Unit 4': ['g', 'b', 'e'],
  'Unit 5': ['h', 'r', 'u'],
  'Unit 6': ['f', 'l', 'w'],
  'Unit 7': ['j', 'k', 'x'],
  'Unit 8': ['v', 'y', 'z'],
  'Unit 9 (Digraphs)': ['sh', 'ch', 'th'],
  'Unit 10': ['wh', 'ck'],
  'Unit 11 (Long e)': ['ee', 'ea'],
  'Unit 12 (Long a)': ['ai', 'ay'],
  'Unit 13 (Long o)': ['oa', 'ow'],
  'Unit 14 (Long i)': ['oo', 'ie', 'igh'],
};

export default function DecodablePage() {
  const [selectedGraphemes, setSelectedGraphemes] = useState<string[]>([
    'm',
    's',
    'a',
    't',
  ]);
  const [sentenceCount, setSentenceCount] = useState(6);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleGenerate = async () => {
    if (selectedGraphemes.length === 0) return;

    setLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/v1/reading/generate_decodable', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          graphemes: selectedGraphemes,
          length_sentences: sentenceCount,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to generate decodable text');
      }

      const data = await response.json();
      setResult(data.text);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      // Demo fallback
      setResult("Sam sat on a mat. The cat sat on the mat. Sam and the cat sat. Is the cat fat? The cat is fat. Sam pats the fat cat.");
    } finally {
      setLoading(false);
    }
  };

  const toggleGrapheme = (grapheme: string) => {
    setSelectedGraphemes((prev) =>
      prev.includes(grapheme)
        ? prev.filter((g) => g !== grapheme)
        : [...prev, grapheme]
    );
  };

  const selectUnit = (graphemes: string[]) => {
    // Add all graphemes from this unit and previous
    const allGraphemes = new Set(selectedGraphemes);
    graphemes.forEach((g) => allGraphemes.add(g));
    setSelectedGraphemes(Array.from(allGraphemes));
  };

  const copyToClipboard = () => {
    if (result) {
      navigator.clipboard.writeText(result);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
            <BookOpen className="w-8 h-8 text-indigo-600" />
            Decodable Text Generator
          </h1>
          <p className="mt-2 text-gray-500">
            Generate phonics-constrained texts based on your scope and sequence.
            Select the graphemes students have learned.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Scope & Sequence */}
          <div className="lg:col-span-2 space-y-6">
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <h3 className="text-lg font-bold text-gray-900 mb-6 flex items-center gap-2">
                <div className="p-2 bg-indigo-100 rounded-lg">
                  <Check className="w-5 h-5 text-indigo-600" />
                </div>
                Scope & Sequence
              </h3>
              <div className="space-y-6">
                {Object.entries(SCOPE_SEQUENCE).map(([unit, graphemes]) => (
                  <div key={unit} className="border-b border-gray-100 pb-4 last:border-0 last:pb-0">
                    <div className="flex items-center justify-between mb-3">
                      <span className="text-sm font-bold text-gray-700 uppercase tracking-wide">
                        {unit}
                      </span>
                      <button
                        onClick={() => selectUnit(graphemes)}
                        className="text-xs font-medium text-indigo-600 hover:text-indigo-700 hover:bg-indigo-50 px-2 py-1 rounded transition-colors flex items-center gap-1"
                      >
                        <Plus className="w-3 h-3" />
                        Add Unit
                      </button>
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {graphemes.map((g) => (
                        <button
                          key={g}
                          onClick={() => toggleGrapheme(g)}
                          className={`px-4 py-2 rounded-lg text-sm font-mono font-bold transition-all ${selectedGraphemes.includes(g)
                              ? 'bg-green-500 text-white shadow-sm ring-2 ring-green-200'
                              : 'bg-gray-50 text-gray-600 hover:bg-gray-100 border border-gray-200'
                            }`}
                        >
                          {g}
                        </button>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Controls */}
          <div className="space-y-6">
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 sticky top-6">
              <div className="mb-6">
                <div className="flex items-center justify-between mb-3">
                  <label className="block text-sm font-bold text-gray-700">
                    Selected Graphemes
                  </label>
                  <button
                    onClick={() => setSelectedGraphemes([])}
                    className="text-xs text-red-500 hover:text-red-700 flex items-center gap-1 font-medium"
                  >
                    <Trash2 className="w-3 h-3" />
                    Clear all
                  </button>
                </div>
                <div className="flex flex-wrap gap-1.5 min-h-[80px] bg-gray-50 p-3 rounded-lg border border-gray-200 content-start">
                  {selectedGraphemes.length === 0 ? (
                    <span className="text-gray-400 text-sm italic w-full text-center mt-4">No graphemes selected</span>
                  ) : (
                    selectedGraphemes.map((g) => (
                      <span
                        key={g}
                        className="px-2.5 py-1 bg-white text-green-700 border border-green-200 rounded-md text-sm font-mono font-bold shadow-sm"
                      >
                        {g}
                      </span>
                    ))
                  )}
                </div>
              </div>

              <div className="mb-8">
                <label htmlFor="sentence-count" className="block text-sm font-bold text-gray-700 mb-3">
                  Length: {sentenceCount} Sentences
                </label>
                <input
                  id="sentence-count"
                  type="range"
                  min="3"
                  max="12"
                  value={sentenceCount}
                  onChange={(e) => setSentenceCount(parseInt(e.target.value))}
                  className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-indigo-600"
                  aria-label="Number of sentences to generate"
                />
                <div className="flex justify-between text-xs text-gray-400 mt-2 font-medium">
                  <span>Short</span>
                  <span>Medium</span>
                  <span>Long</span>
                </div>
              </div>

              <button
                onClick={handleGenerate}
                disabled={loading || selectedGraphemes.length === 0}
                className="w-full px-6 py-3 bg-indigo-600 text-white font-bold rounded-lg hover:bg-indigo-700 
                         transition-colors disabled:opacity-50 disabled:cursor-not-allowed shadow-sm flex items-center justify-center gap-2"
              >
                {loading ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    Generating...
                  </>
                ) : (
                  <>
                    <BookOpen className="w-5 h-5" />
                    Generate Text
                  </>
                )}
              </button>
            </div>
          </div>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg flex items-center gap-2">
            <span className="font-bold">Error:</span> {error}
          </div>
        )}

        {result && (
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-8">
            <div className="flex items-center justify-between mb-6 border-b border-gray-100 pb-4">
              <h2 className="text-xl font-bold text-gray-900 flex items-center gap-2">
                <div className="p-2 bg-green-100 rounded-lg">
                  <BookOpen className="w-5 h-5 text-green-600" />
                </div>
                Generated Decodable Text
              </h2>
              <div className="flex space-x-3">
                <button
                  onClick={handleGenerate}
                  className="px-4 py-2 bg-white border border-gray-200 text-gray-700 font-medium rounded-lg hover:bg-gray-50 transition-colors flex items-center gap-2 shadow-sm"
                >
                  <RefreshCw className="w-4 h-4" />
                  Regenerate
                </button>
                <button
                  onClick={copyToClipboard}
                  className="px-4 py-2 bg-indigo-50 border border-indigo-100 text-indigo-700 font-medium rounded-lg hover:bg-indigo-100 transition-colors flex items-center gap-2 shadow-sm"
                >
                  <Copy className="w-4 h-4" />
                  Copy Text
                </button>
              </div>
            </div>
            
            <div className="bg-yellow-50 p-8 rounded-xl border border-yellow-100 shadow-inner">
              <p className="text-2xl leading-relaxed font-serif text-gray-900">{result}</p>
            </div>
            
            <div className="mt-6 flex items-center gap-6 text-sm font-medium text-gray-500 border-t border-gray-100 pt-4">
              <div className="flex items-center gap-2">
                <span className="w-2 h-2 bg-indigo-400 rounded-full"></span>
                {result.split(/\s+/).filter(Boolean).length} words
              </div>
              <div className="flex items-center gap-2">
                <span className="w-2 h-2 bg-indigo-400 rounded-full"></span>
                {result.split(/[.!?]+/).filter(Boolean).length} sentences
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
