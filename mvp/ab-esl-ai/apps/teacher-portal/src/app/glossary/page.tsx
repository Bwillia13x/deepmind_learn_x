"use client";

import { useState } from 'react';
import { Loader2, Copy, Download, Languages, BookOpen, Sparkles, Check, Printer } from 'lucide-react';

interface GlossEntry {
  en: string;
  l1: string;
  definition?: string;
}

interface GlossResult {
  translation: string;
  gloss: GlossEntry[];
}

const LANGUAGES = [
  { code: 'ar', name: 'Arabic', dir: 'rtl' },
  { code: 'uk', name: 'Ukrainian', dir: 'ltr' },
  { code: 'es', name: 'Spanish', dir: 'ltr' },
  { code: 'zh', name: 'Chinese', dir: 'ltr' },
  { code: 'tl', name: 'Tagalog', dir: 'ltr' },
  { code: 'pa', name: 'Punjabi', dir: 'ltr' },
];

const SAMPLE_TEXTS = [
  {
    title: 'Math - Fractions',
    text: 'A fraction represents part of a whole number. The top number is called the numerator. The bottom number is called the denominator.',
  },
  {
    title: 'Science - Water Cycle',
    text: 'Water evaporates from lakes and oceans. It rises into the sky and forms clouds. When clouds get heavy, precipitation falls as rain or snow.',
  },
  {
    title: 'Classroom Instructions',
    text: 'Please open your textbooks to page twenty-five. Read the passage quietly. Then answer the questions at the bottom of the page.',
  },
];

export default function GlossaryPage() {
  const [text, setText] = useState('');
  const [l1, setL1] = useState('ar');
  const [topK, setTopK] = useState(10);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<GlossResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  const handleSubmit = async () => {
    if (!text.trim()) return;

    setLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/v1/captions/gloss', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text, l1, top_k: topK }),
      });

      if (!response.ok) {
        throw new Error('Failed to generate glossary');
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      // Demo fallback
      setResult({
        translation: l1 === 'ar' 
          ? 'الكسر يمثل جزءاً من عدد صحيح. الرقم العلوي يسمى البسط. الرقم السفلي يسمى المقام.' 
          : 'Una fracción representa parte de un número entero. El número superior se llama numerador. El número inferior se llama denominador.',
        gloss: [
          { en: 'fraction', l1: l1 === 'ar' ? 'كسر' : 'fracción' },
          { en: 'whole number', l1: l1 === 'ar' ? 'عدد صحيح' : 'número entero' },
          { en: 'numerator', l1: l1 === 'ar' ? 'بسط' : 'numerador' },
          { en: 'denominator', l1: l1 === 'ar' ? 'مقام' : 'denominador' },
        ]
      });
    } finally {
      setLoading(false);
    }
  };

  const copyGlossary = () => {
    if (!result) return;
    const glossText = result.gloss.map((g) => `${g.en} - ${g.l1}`).join('\n');
    navigator.clipboard.writeText(glossText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const downloadCSV = () => {
    if (!result) return;
    const csv = [
      'English,Translation',
      ...result.gloss.map((g) => `"${g.en}","${g.l1}"`),
    ].join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `glossary-${l1}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const selectedLang = LANGUAGES.find((lang) => lang.code === l1);

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
            <Languages className="w-8 h-8 text-indigo-600" />
            Translation & Glossary
          </h1>
          <p className="mt-2 text-gray-500">
            Generate bilingual glossaries and translations for any content. Perfect for
            creating vocabulary lists and translated materials.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Input Section */}
          <div className="lg:col-span-2 space-y-6">
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <label className="block text-sm font-bold text-gray-700 mb-3">
                English Text
              </label>
              <textarea
                value={text}
                onChange={(e) => setText(e.target.value)}
                className="w-full min-h-[200px] p-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none transition-all resize-y text-gray-700 leading-relaxed"
                placeholder="Enter or paste English text to translate and create a glossary..."
              />
              <div className="mt-4 flex items-center justify-between">
                <span className="text-sm font-medium text-gray-500 bg-gray-50 px-3 py-1 rounded-full border border-gray-100">
                  {text.split(/\s+/).filter(Boolean).length} words
                </span>
                <div className="flex flex-wrap gap-2 items-center">
                  <span className="text-xs font-bold text-gray-400 uppercase tracking-wide mr-1">Quick fill:</span>
                  {SAMPLE_TEXTS.map((sample, idx) => (
                    <button
                      key={idx}
                      onClick={() => setText(sample.text)}
                      className="text-xs px-3 py-1.5 bg-gray-50 hover:bg-gray-100 border border-gray-200 rounded-lg text-gray-600 font-medium transition-colors"
                    >
                      {sample.title}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Controls */}
          <div className="space-y-6">
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 sticky top-6">
              <div className="space-y-6">
                <div>
                  <label htmlFor="target-language" className="block text-sm font-bold text-gray-700 mb-2">
                    Target Language
                  </label>
                  <div className="relative">
                    <select
                      id="target-language"
                      value={l1}
                      onChange={(e) => setL1(e.target.value)}
                      className="w-full appearance-none bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-indigo-500 focus:border-indigo-500 block p-3 pr-8"
                      aria-label="Select target language for glossary"
                    >
                      {LANGUAGES.map((lang) => (
                        <option key={lang.code} value={lang.code}>
                          {lang.name}
                        </option>
                      ))}
                    </select>
                    <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-3 text-gray-500">
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7"></path></svg>
                    </div>
                  </div>
                </div>

                <div>
                  <label htmlFor="vocab-count" className="block text-sm font-bold text-gray-700 mb-3">
                    Vocabulary Words (max): {topK}
                  </label>
                  <input
                    id="vocab-count"
                    type="range"
                    min="5"
                    max="20"
                    value={topK}
                    onChange={(e) => setTopK(parseInt(e.target.value))}
                    className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-indigo-600"
                    aria-label="Maximum vocabulary words to generate"
                  />
                  <div className="flex justify-between text-xs text-gray-400 mt-2 font-medium">
                    <span>5</span>
                    <span>10</span>
                    <span>15</span>
                    <span>20</span>
                  </div>
                </div>

                <button
                  onClick={handleSubmit}
                  disabled={loading || !text.trim()}
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
                      <Sparkles className="w-5 h-5" />
                      Generate Glossary
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg flex items-center gap-2">
            <span className="font-bold">Error:</span> {error}
          </div>
        )}

        {result && (
          <div className="space-y-8">
            {/* Translation */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <div className="flex items-center justify-between mb-4 border-b border-gray-100 pb-4">
                <h2 className="text-xl font-bold text-gray-900 flex items-center gap-2">
                  <div className="p-2 bg-blue-100 rounded-lg">
                    <Languages className="w-5 h-5 text-blue-600" />
                  </div>
                  Translation
                </h2>
                <button
                  onClick={() => navigator.clipboard.writeText(result.translation)}
                  className="p-2 text-gray-500 hover:text-indigo-600 hover:bg-indigo-50 rounded-lg transition-colors"
                  title="Copy translation"
                >
                  <Copy className="w-5 h-5" />
                </button>
              </div>
              <div
                className={`bg-blue-50 p-6 rounded-xl text-lg leading-relaxed text-blue-900 border border-blue-100 ${selectedLang?.dir === 'rtl' ? 'text-right font-arabic' : ''
                  }`}
                dir={selectedLang?.dir}
              >
                {result.translation}
              </div>
            </div>

            {/* Glossary */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <div className="flex items-center justify-between mb-6 border-b border-gray-100 pb-4">
                <h2 className="text-xl font-bold text-gray-900 flex items-center gap-2">
                  <div className="p-2 bg-green-100 rounded-lg">
                    <BookOpen className="w-5 h-5 text-green-600" />
                  </div>
                  Vocabulary Glossary ({result.gloss.length} words)
                </h2>
                <div className="flex space-x-3">
                  <button
                    onClick={copyGlossary}
                    className="px-4 py-2 bg-white border border-gray-200 text-gray-700 font-medium rounded-lg hover:bg-gray-50 transition-colors flex items-center gap-2 shadow-sm"
                  >
                    {copied ? <Check className="w-4 h-4 text-green-600" /> : <Copy className="w-4 h-4" />}
                    {copied ? 'Copied!' : 'Copy List'}
                  </button>
                  <button
                    onClick={downloadCSV}
                    className="px-4 py-2 bg-indigo-50 border border-indigo-100 text-indigo-700 font-medium rounded-lg hover:bg-indigo-100 transition-colors flex items-center gap-2 shadow-sm"
                  >
                    <Download className="w-4 h-4" />
                    Export CSV
                  </button>
                </div>
              </div>

              {result.gloss.length > 0 ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {result.gloss.map((entry, idx) => (
                    <div
                      key={idx}
                      className="flex items-center justify-between bg-gray-50 p-4 rounded-xl border border-gray-100 hover:border-indigo-200 hover:shadow-sm transition-all group"
                    >
                      <span className="font-bold text-gray-900">{entry.en}</span>
                      <div className="flex items-center gap-3">
                        <span className="text-gray-300 group-hover:text-indigo-300 transition-colors">→</span>
                        <span
                          className={`text-indigo-700 font-bold ${selectedLang?.dir === 'rtl' ? 'text-right font-arabic' : ''
                            }`}
                          dir={selectedLang?.dir}
                        >
                          {entry.l1}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-12 bg-gray-50 rounded-xl border border-dashed border-gray-200">
                  <p className="text-gray-500 font-medium">
                    No vocabulary words found. Try adding more content-specific terms.
                  </p>
                </div>
              )}
            </div>

            {/* Print hint */}
            <div className="flex items-center justify-center gap-2 text-sm text-gray-500 bg-gray-100 p-4 rounded-xl border border-gray-200">
              <Printer className="w-4 h-4" />
              <p>
                <strong>Tip:</strong> Use Ctrl+P (Cmd+P on Mac) to print this glossary for classroom use.
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
