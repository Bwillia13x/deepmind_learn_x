"use client";

import { useState } from "react";
import { Wand2, Copy, Download, BookOpen, HelpCircle, Languages, Check, AlertCircle, ArrowRight, FileText } from "lucide-react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface LeveledOutput {
  target: string;
  text: string;
  questions: (string | { type?: string; q: string; a?: string })[];
  gloss: { en: string; l1: string; definition?: string }[];
}

export default function LevelerPage() {
  const [inputText, setInputText] = useState("");
  const [selectedLevels, setSelectedLevels] = useState<string[]>(["A2", "B1"]);
  const [l1, setL1] = useState("es");
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<LeveledOutput[]>([]);
  const [error, setError] = useState("");
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null);

  const availableLevels = ["A1", "A2", "B1", "B2", "Gr3", "Gr4", "Gr5", "Gr6", "Gr7", "Gr8"];
  const availableL1s = [
    { code: "ar", name: "Arabic" },
    { code: "es", name: "Spanish" },
    { code: "zh", name: "Chinese" },
    { code: "fr", name: "French" },
  ];

  const toggleLevel = (level: string) => {
    setSelectedLevels((prev) =>
      prev.includes(level) ? prev.filter((l) => l !== level) : [...prev, level]
    );
  };

  const handleGenerate = async () => {
    if (!inputText.trim()) {
      setError("Please enter some text to level.");
      return;
    }
    if (selectedLevels.length === 0) {
      setError("Please select at least one target level.");
      return;
    }

    setLoading(true);
    setError("");
    setResults([]);

    try {
      const response = await fetch(`${API_URL}/v1/authoring/level-text`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          text: inputText,
          targets: selectedLevels,
          l1,
        }),
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.statusText}`);
      }

      const data = await response.json();
      setResults(data.levels || []);
    } catch (err: any) {
      setError(err.message || "Failed to generate leveled texts");
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = (text: string, index: number) => {
    navigator.clipboard.writeText(text);
    setCopiedIndex(index);
    setTimeout(() => setCopiedIndex(null), 2000);
  };

  const downloadJSON = () => {
    const dataStr = JSON.stringify({ input: inputText, levels: results }, null, 2);
    const blob = new Blob([dataStr], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "leveled-texts.json";
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-6xl mx-auto space-y-8">
        <header>
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
            <Wand2 className="w-8 h-8 text-indigo-600" />
            Text Leveler
          </h1>
          <p className="text-gray-500 mt-2 text-lg">
            Generate multiple reading levels from one text with comprehension questions and glossary.
          </p>
        </header>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
          <div className="p-6 border-b border-gray-100">
            <h2 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
              <FileText className="w-5 h-5 text-gray-500" />
              Input Text
            </h2>
          </div>

          <div className="p-6 space-y-6">
            <textarea
              className="w-full h-40 p-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-colors font-mono text-sm resize-y"
              placeholder="Paste the text you want to level here..."
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
            />

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              <div className="space-y-3">
                <label className="block text-sm font-medium text-gray-700">Target Levels</label>
                <div className="flex flex-wrap gap-2">
                  {availableLevels.map((level) => (
                    <button
                      key={level}
                      onClick={() => toggleLevel(level)}
                      className={`px-4 py-2 rounded-lg font-medium text-sm transition-all border ${selectedLevels.includes(level)
                        ? "bg-indigo-600 text-white border-indigo-600 shadow-sm"
                        : "bg-white text-gray-600 border-gray-200 hover:border-indigo-300 hover:bg-indigo-50"
                        }`}
                    >
                      {level}
                    </button>
                  ))}
                </div>
              </div>

              <div className="space-y-3">
                <label htmlFor="glossary-language" className="block text-sm font-medium text-gray-700">
                  Glossary Language (L1)
                </label>
                <div className="relative">
                  <Languages className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                  <select
                    id="glossary-language"
                    className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-colors appearance-none bg-white"
                    value={l1}
                    onChange={(e) => setL1(e.target.value)}
                  >
                    {availableL1s.map((lang) => (
                      <option key={lang.code} value={lang.code}>
                        {lang.name}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
            </div>

            <button
              onClick={handleGenerate}
              disabled={loading}
              className="w-full bg-indigo-600 text-white font-semibold py-4 rounded-lg hover:bg-indigo-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed shadow-sm flex items-center justify-center gap-2 text-lg"
            >
              {loading ? (
                <>
                  <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  Generating...
                </>
              ) : (
                <>
                  <Wand2 className="w-5 h-5" />
                  Generate Leveled Texts
                </>
              )}
            </button>

            {error && (
              <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 flex items-center gap-2">
                <AlertCircle className="w-5 h-5 flex-shrink-0" />
                {error}
              </div>
            )}
          </div>
        </div>

        {results.length > 0 && (
          <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <div className="flex justify-between items-center border-b border-gray-200 pb-4">
              <h2 className="text-2xl font-bold text-gray-900">Results</h2>
              <button
                onClick={downloadJSON}
                className="px-4 py-2 bg-white border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors shadow-sm font-medium flex items-center gap-2"
              >
                <Download className="w-4 h-4" />
                Download JSON
              </button>
            </div>

            {results.map((result, idx) => (
              <div key={idx} className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
                <div className="p-6 border-b border-gray-100 flex justify-between items-center bg-gray-50/50">
                  <div className="flex items-center gap-3">
                    <span className="bg-indigo-100 text-indigo-700 px-3 py-1 rounded-full font-bold text-sm border border-indigo-200">
                      Level {result.target}
                    </span>
                  </div>
                  <button
                    onClick={() => copyToClipboard(result.text, idx)}
                    className="text-indigo-600 hover:text-indigo-700 font-medium text-sm flex items-center gap-1.5 hover:bg-indigo-50 px-3 py-1.5 rounded-lg transition-colors"
                  >
                    {copiedIndex === idx ? (
                      <>
                        <Check className="w-4 h-4" />
                        Copied!
                      </>
                    ) : (
                      <>
                        <Copy className="w-4 h-4" />
                        Copy Text
                      </>
                    )}
                  </button>
                </div>

                <div className="p-8">
                  <div className="prose max-w-none mb-8 bg-gray-50 p-6 rounded-xl border border-gray-100">
                    <p className="text-gray-800 leading-loose text-lg whitespace-pre-wrap">{result.text}</p>
                  </div>

                  <div className="grid md:grid-cols-2 gap-8">
                    {result.questions && result.questions.length > 0 && (
                      <div>
                        <h4 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
                          <HelpCircle className="w-5 h-5 text-indigo-600" />
                          Comprehension Questions
                        </h4>
                        <ul className="space-y-3">
                          {result.questions.map((q, qIdx) => (
                            <li key={qIdx} className="flex gap-3 text-gray-700 bg-white p-4 rounded-lg border border-gray-100 shadow-sm">
                              <span className="font-bold text-indigo-400 min-w-[1.5rem]">{qIdx + 1}.</span>
                              <span>{typeof q === 'string' ? q : q.q}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {result.gloss && result.gloss.length > 0 && (
                      <div>
                        <h4 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
                          <BookOpen className="w-5 h-5 text-indigo-600" />
                          Glossary
                        </h4>
                        <div className="grid grid-cols-1 gap-2">
                          {result.gloss.map((entry, gIdx) => (
                            <div key={gIdx} className="bg-white p-3 rounded-lg border border-gray-100 shadow-sm flex justify-between items-center group hover:border-indigo-200 transition-colors">
                              <span className="font-medium text-gray-900">{entry.en}</span>
                              <div className="flex items-center gap-2">
                                <ArrowRight className="w-4 h-4 text-gray-300 group-hover:text-indigo-300 transition-colors" />
                                <span className="text-indigo-600 font-medium">{entry.l1}</span>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

