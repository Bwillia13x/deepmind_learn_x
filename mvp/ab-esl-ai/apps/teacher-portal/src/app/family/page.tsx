"use client";

import { useState } from 'react';
import { Users, MessageCircle, Heart, Send, Gift, Globe, ArrowRight, Copy, Printer, Mail } from 'lucide-react';

const LANGUAGES = [
    { code: 'ar', name: 'Arabic', flag: '🇸🇦', dir: 'rtl' },
    { code: 'zh', name: 'Chinese', flag: '🇨🇳', dir: 'ltr' },
    { code: 'es', name: 'Spanish', flag: '🇪🇸', dir: 'ltr' },
    { code: 'uk', name: 'Ukrainian', flag: '🇺🇦', dir: 'ltr' },
    { code: 'tl', name: 'Tagalog', flag: '🇵🇭', dir: 'ltr' },
    { code: 'pa', name: 'Punjabi', flag: '🇮🇳', dir: 'ltr' },
    { code: 'so', name: 'Somali', flag: '🇸🇴', dir: 'ltr' },
    { code: 'vi', name: 'Vietnamese', flag: '🇻🇳', dir: 'ltr' },
    { code: 'fa', name: 'Farsi', flag: '🇮🇷', dir: 'rtl' },
];

interface HomeworkHelper {
    student_version: {
        title: string;
        instructions: string;
        content: string;
    };
    parent_version: {
        instructions_l1: string;
        key_vocabulary: { word: string; translation: string }[];
        encouragement_phrases: string[];
    };
    shared_activity: {
        title: string;
        description: string;
        materials_needed: string[];
    };
}

interface MicroLesson {
    topic: string;
    sms_message: string;
    voice_script: string;
    practice_activity: string;
    celebration_message: string;
}

interface Celebration {
    title_l1: string;
    message_l1: string;
    message_en: string;
    celebration_emoji: string;
    share_message: string;
}

export default function FamilyLiteracyPage() {
    const [selectedL1, setSelectedL1] = useState('ar');
    const [homeworkTitle, setHomeworkTitle] = useState('');
    const [homeworkContent, setHomeworkContent] = useState('');
    const [helper, setHelper] = useState<HomeworkHelper | null>(null);
    const [microLesson, setMicroLesson] = useState<MicroLesson | null>(null);
    const [lessonTopic, setLessonTopic] = useState('');
    const [loading, setLoading] = useState(false);
    const [celebrationStudent, setCelebrationStudent] = useState('');
    const [celebrationAchievement, setCelebrationAchievement] = useState('');
    const [celebration, setCelebration] = useState<Celebration | null>(null);

    const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    const selectedLang = LANGUAGES.find(l => l.code === selectedL1);

    const generateHomeworkHelper = async () => {
        if (!homeworkTitle.trim()) return;
        setLoading(true);
        try {
            const res = await fetch(`${API_URL}/v1/family/homework-helper`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    l1_code: selectedL1,
                    assignment_title: homeworkTitle,
                    assignment_content: homeworkContent,
                }),
            });
            if (res.ok) {
                const data = await res.json();
                setHelper(data);
            }
        } catch (error) {
            console.error('Error generating helper:', error);
            // Demo fallback
            setHelper({
                student_version: {
                    title: homeworkTitle,
                    instructions: 'Read the passage and answer the questions below.',
                    content: homeworkContent || 'Complete the reading assignment.',
                },
                parent_version: {
                    instructions_l1: selectedL1 === 'ar'
                        ? 'اقرأ مع طفلك واساعده في الإجابة على الأسئلة'
                        : selectedL1 === 'es'
                            ? 'Lea con su hijo y ayúdelo a responder las preguntas'
                            : selectedL1 === 'uk'
                                ? 'Читайте з дитиною та допоможіть відповісти на запитання'
                                : 'Read with your child and help them answer the questions',
                    key_vocabulary: [
                        { word: 'understand', translation: selectedL1 === 'ar' ? 'يفهم' : selectedL1 === 'es' ? 'entender' : 'understand' },
                        { word: 'answer', translation: selectedL1 === 'ar' ? 'إجابة' : selectedL1 === 'es' ? 'respuesta' : 'answer' },
                        { word: 'question', translation: selectedL1 === 'ar' ? 'سؤال' : selectedL1 === 'es' ? 'pregunta' : 'question' },
                    ],
                    encouragement_phrases: [
                        selectedL1 === 'ar' ? 'أحسنت! أنت تتعلم جيداً' : selectedL1 === 'es' ? '¡Muy bien! Estás aprendiendo' : 'Great job! You are learning well',
                        selectedL1 === 'ar' ? 'حاول مرة أخرى' : selectedL1 === 'es' ? 'Intenta otra vez' : 'Try again',
                        selectedL1 === 'ar' ? 'أنا فخور بك' : selectedL1 === 'es' ? 'Estoy orgulloso de ti' : 'I am proud of you',
                    ],
                },
                shared_activity: {
                    title: 'Family Reading Time',
                    description: 'Read together for 10 minutes. Take turns reading sentences.',
                    materials_needed: ['The homework passage', 'A quiet space', 'Optional: bookmarks or sticky notes'],
                },
            });
        }
        setLoading(false);
    };

    const generateMicroLesson = async () => {
        if (!lessonTopic.trim()) return;
        setLoading(true);
        try {
            const res = await fetch(`${API_URL}/v1/family/micro-lesson`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    l1_code: selectedL1,
                    topic: lessonTopic,
                }),
            });
            if (res.ok) {
                const data = await res.json();
                setMicroLesson(data);
            }
        } catch (error) {
            console.error('Error generating micro-lesson:', error);
            // Demo fallback
            const todayLesson = selectedL1 === 'ar' ? 'درس اليوم' : selectedL1 === 'es' ? 'Lección de hoy' : "Today's lesson";
            const congrats = selectedL1 === 'ar' ? 'مبروك!' : selectedL1 === 'es' ? '¡Felicidades!' : 'Congratulations!';
            setMicroLesson({
                topic: lessonTopic,
                sms_message: `📚 Today's English: ${lessonTopic}\n\n${todayLesson}\n\n🏠 Practice: Ask your child to use this word in a sentence.\n\nReply DONE when finished! ✅`,
                voice_script: `Hello! Today we will practice the word "${lessonTopic}". Listen and repeat after your child. This helps them learn!`,
                practice_activity: 'Use the word 3 times at dinner tonight',
                celebration_message: `🎉 ${congrats} Your child completed today's lesson!`,
            });
        }
        setLoading(false);
    };

    const generateCelebration = async () => {
        if (!celebrationStudent.trim() || !celebrationAchievement.trim()) return;
        setLoading(true);
        try {
            const res = await fetch(`${API_URL}/v1/family/progress-celebration`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    l1_code: selectedL1,
                    student_name: celebrationStudent,
                    achievement: celebrationAchievement,
                }),
            });
            if (res.ok) {
                const data = await res.json();
                setCelebration(data);
            }
        } catch (error) {
            console.error('Error generating celebration:', error);
            // Demo fallback
            setCelebration({
                title_l1: selectedL1 === 'ar' ? 'تهانينا!' : selectedL1 === 'es' ? '¡Felicitaciones!' : 'Congratulations!',
                message_l1: selectedL1 === 'ar'
                    ? `${celebrationStudent} حقق إنجازاً رائعاً: ${celebrationAchievement}!`
                    : selectedL1 === 'es'
                        ? `${celebrationStudent} logró algo increíble: ${celebrationAchievement}!`
                        : `${celebrationStudent} achieved something great: ${celebrationAchievement}!`,
                message_en: `${celebrationStudent} achieved: ${celebrationAchievement}!`,
                celebration_emoji: '🎉🌟🏆',
                share_message: `Proud of ${celebrationStudent}! ${celebrationAchievement} #ABESLsuccess`,
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
                        <Users className="w-8 h-8 text-indigo-600" />
                        Family Literacy Co-Pilot
                    </h1>
                    <p className="mt-2 text-gray-500">
                        Engage families in literacy development with bilingual support and culturally responsive communication.
                    </p>
                </div>

                {/* Language Selector */}
                <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                    <h2 className="text-lg font-bold text-gray-900 flex items-center gap-2 mb-4">
                        <Globe className="w-5 h-5 text-indigo-600" />
                        Select Family&apos;s Home Language
                    </h2>
                    <div className="flex flex-wrap gap-3">
                        {LANGUAGES.map((lang) => (
                            <button
                                key={lang.code}
                                onClick={() => setSelectedL1(lang.code)}
                                className={`px-4 py-2.5 rounded-lg border transition-all flex items-center gap-3 ${selectedL1 === lang.code
                                    ? 'border-indigo-500 bg-indigo-50 text-indigo-700 ring-1 ring-indigo-500'
                                    : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50 text-gray-600'
                                    }`}
                            >
                                <span className="text-2xl">{lang.flag}</span>
                                <span className="font-medium">{lang.name}</span>
                            </button>
                        ))}
                    </div>
                </div>

                <div className="grid lg:grid-cols-2 gap-8">
                    {/* Homework Helper */}
                    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                        <h2 className="text-lg font-bold text-gray-900 flex items-center gap-2 mb-6">
                            <div className="p-2 bg-blue-100 rounded-lg">
                                <MessageCircle className="w-5 h-5 text-blue-600" />
                            </div>
                            Bilingual Homework Helper
                        </h2>
                        <div className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">Assignment Title</label>
                                <input
                                    type="text"
                                    value={homeworkTitle}
                                    onChange={(e) => setHomeworkTitle(e.target.value)}
                                    placeholder="e.g., Reading Comprehension - The Water Cycle"
                                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none transition-all"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">Assignment Content (optional)</label>
                                <textarea
                                    value={homeworkContent}
                                    onChange={(e) => setHomeworkContent(e.target.value)}
                                    placeholder="Paste the homework instructions or content..."
                                    className="w-full h-32 p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none transition-all resize-none"
                                />
                            </div>
                            <div className="flex justify-end">
                                <button
                                    onClick={generateHomeworkHelper}
                                    disabled={loading || !homeworkTitle.trim()}
                                    className="px-6 py-2.5 bg-indigo-600 text-white font-medium rounded-lg hover:bg-indigo-700 
                                             transition-colors disabled:opacity-50 disabled:cursor-not-allowed shadow-sm flex items-center gap-2"
                                >
                                    Generate Bilingual Helper
                                    <ArrowRight className="w-4 h-4" />
                                </button>
                            </div>
                        </div>

                        {helper && (
                            <div className="mt-8 space-y-6">
                                {/* Student Version */}
                                <div className="p-4 bg-blue-50 rounded-lg border border-blue-100">
                                    <h3 className="font-bold text-blue-900 mb-2 flex items-center gap-2">
                                        <span>📖</span> Student Version (English)
                                    </h3>
                                    <p className="font-semibold text-blue-800">{helper.student_version.title}</p>
                                    <p className="text-sm text-blue-700 mt-2">{helper.student_version.instructions}</p>
                                </div>

                                {/* Parent Version */}
                                <div className={`p-4 bg-green-50 rounded-lg border border-green-100 ${selectedLang?.dir === 'rtl' ? 'text-right' : ''}`}>
                                    <h3 className="font-bold text-green-900 mb-2 flex items-center gap-2">
                                        <span>👨‍👩‍👧</span> Parent Version ({selectedLang?.name})
                                    </h3>
                                    <p className={`text-lg text-green-800 ${selectedLang?.dir === 'rtl' ? 'font-arabic' : ''}`}>
                                        {helper.parent_version.instructions_l1}
                                    </p>

                                    <div className="mt-4">
                                        <p className="text-sm font-bold text-green-900 mb-2">Key Vocabulary:</p>
                                        <div className="space-y-2">
                                            {helper.parent_version.key_vocabulary.map((v, i) => (
                                                <div key={i} className="flex justify-between text-sm bg-white p-2 rounded border border-green-100">
                                                    <span className="font-medium text-gray-900">{v.word}</span>
                                                    <span className="text-gray-600">{v.translation}</span>
                                                </div>
                                            ))}
                                        </div>
                                    </div>

                                    <div className="mt-4">
                                        <p className="text-sm font-bold text-green-900 mb-2">Encouragement Phrases:</p>
                                        <ul className="space-y-1">
                                            {helper.parent_version.encouragement_phrases.map((phrase, i) => (
                                                <li key={i} className="text-sm text-green-700">✨ {phrase}</li>
                                            ))}
                                        </ul>
                                    </div>
                                </div>

                                {/* Shared Activity */}
                                <div className="p-4 bg-purple-50 rounded-lg border border-purple-100">
                                    <h3 className="font-bold text-purple-900 mb-2 flex items-center gap-2">
                                        <span>🏠</span> Shared Family Activity
                                    </h3>
                                    <p className="font-semibold text-purple-800">{helper.shared_activity.title}</p>
                                    <p className="text-sm text-purple-700 mt-1">{helper.shared_activity.description}</p>
                                    <div className="mt-3 pt-3 border-t border-purple-100">
                                        <p className="text-xs font-bold text-purple-900 uppercase tracking-wide mb-1">Materials needed</p>
                                        <p className="text-sm text-purple-700">{helper.shared_activity.materials_needed.join(', ')}</p>
                                    </div>
                                </div>
                            </div>
                        )}
                    </div>

                    <div className="space-y-8">
                        {/* SMS Micro-Lesson */}
                        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                            <h2 className="text-lg font-bold text-gray-900 flex items-center gap-2 mb-6">
                                <div className="p-2 bg-green-100 rounded-lg">
                                    <Send className="w-5 h-5 text-green-600" />
                                </div>
                                SMS Micro-Lesson Generator
                            </h2>
                            <p className="text-sm text-gray-500 mb-4">
                                Generate brief lessons that can be delivered via SMS or WhatsApp—no app required.
                            </p>
                            <div className="flex gap-3">
                                <input
                                    type="text"
                                    value={lessonTopic}
                                    onChange={(e) => setLessonTopic(e.target.value)}
                                    placeholder="Enter topic (e.g., 'weather words')"
                                    className="flex-1 border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none transition-all"
                                />
                                <button
                                    onClick={generateMicroLesson}
                                    disabled={loading || !lessonTopic.trim()}
                                    className="px-4 py-2 bg-indigo-600 text-white font-medium rounded-lg hover:bg-indigo-700 
                                             transition-colors disabled:opacity-50 disabled:cursor-not-allowed shadow-sm"
                                >
                                    Generate
                                </button>
                            </div>

                            {microLesson && (
                                <div className="mt-6 space-y-4">
                                    <div className="p-4 bg-gray-50 rounded-lg border border-gray-200 font-mono text-sm whitespace-pre-wrap text-gray-700 relative group">
                                        <button
                                            className="absolute top-2 right-2 p-1.5 text-gray-400 hover:text-gray-600 hover:bg-gray-200 rounded transition-colors"
                                            aria-label="Copy message"
                                            title="Copy message"
                                        >
                                            <Copy className="w-4 h-4" />
                                        </button>
                                        {microLesson.sms_message}
                                    </div>
                                    <div className="grid grid-cols-1 gap-4">
                                        <div className="p-3 bg-green-50 rounded-lg border border-green-100">
                                            <p className="text-xs font-bold text-green-800 uppercase tracking-wide mb-1">Voice Script (for low-literacy parents)</p>
                                            <p className="text-sm text-green-700">{microLesson.voice_script}</p>
                                        </div>
                                        <div className="p-3 bg-blue-50 rounded-lg border border-blue-100">
                                            <p className="text-xs font-bold text-blue-800 uppercase tracking-wide mb-1">Home Practice Activity</p>
                                            <p className="text-sm text-blue-700">{microLesson.practice_activity}</p>
                                        </div>
                                    </div>
                                </div>
                            )}
                        </div>

                        {/* Progress Celebration */}
                        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                            <h2 className="text-lg font-bold text-gray-900 flex items-center gap-2 mb-6">
                                <div className="p-2 bg-yellow-100 rounded-lg">
                                    <Gift className="w-5 h-5 text-yellow-600" />
                                </div>
                                Progress Celebration
                            </h2>
                            <div className="space-y-4">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-2">Student Name</label>
                                    <input
                                        type="text"
                                        value={celebrationStudent}
                                        onChange={(e) => setCelebrationStudent(e.target.value)}
                                        placeholder="Student's first name"
                                        className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none transition-all"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-2">Achievement</label>
                                    <input
                                        type="text"
                                        value={celebrationAchievement}
                                        onChange={(e) => setCelebrationAchievement(e.target.value)}
                                        placeholder="e.g., 'Read 50 books this month!'"
                                        className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none transition-all"
                                    />
                                </div>
                                <button
                                    onClick={generateCelebration}
                                    disabled={loading || !celebrationStudent.trim() || !celebrationAchievement.trim()}
                                    className="w-full px-6 py-2.5 bg-indigo-600 text-white font-medium rounded-lg hover:bg-indigo-700 
                                             transition-colors disabled:opacity-50 disabled:cursor-not-allowed shadow-sm"
                                >
                                    Generate Celebration
                                </button>
                            </div>

                            {celebration && (
                                <div className="mt-6 p-6 bg-gradient-to-br from-yellow-50 to-pink-50 rounded-xl border border-yellow-100 text-center">
                                    <div className="text-5xl mb-4 animate-bounce">{celebration.celebration_emoji}</div>
                                    <h3 className="text-2xl font-bold text-gray-900 mb-2">{celebration.title_l1}</h3>
                                    <p className={`text-lg text-gray-800 mb-3 ${selectedLang?.dir === 'rtl' ? 'font-arabic' : ''}`}>
                                        {celebration.message_l1}
                                    </p>
                                    <p className="text-sm text-gray-500 mb-6">{celebration.message_en}</p>
                                    <div className="flex justify-center gap-3">
                                        <button className="p-2 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 text-gray-600 transition-colors" title="Send via SMS">
                                            <MessageCircle className="w-5 h-5" />
                                        </button>
                                        <button className="p-2 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 text-gray-600 transition-colors" title="Send via Email">
                                            <Mail className="w-5 h-5" />
                                        </button>
                                        <button className="p-2 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 text-gray-600 transition-colors" title="Print Certificate">
                                            <Printer className="w-5 h-5" />
                                        </button>
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>
                </div>

                {/* Tips Section */}
                <div className="bg-pink-50 rounded-xl border border-pink-100 p-6">
                    <h2 className="text-lg font-bold text-pink-900 flex items-center gap-2 mb-4">
                        <Heart className="w-5 h-5 text-pink-600" />
                        Family Engagement Tips
                    </h2>
                    <div className="grid md:grid-cols-2 gap-6 text-sm">
                        <div>
                            <h3 className="font-bold text-pink-800 mb-2 uppercase tracking-wide text-xs">For Low-Literacy Parents</h3>
                            <ul className="space-y-2 text-pink-700">
                                <li className="flex items-start gap-2">
                                    <span className="mt-1 w-1.5 h-1.5 bg-pink-400 rounded-full flex-shrink-0" />
                                    Use voice messages instead of text
                                </li>
                                <li className="flex items-start gap-2">
                                    <span className="mt-1 w-1.5 h-1.5 bg-pink-400 rounded-full flex-shrink-0" />
                                    Include pictures and emojis to convey meaning
                                </li>
                                <li className="flex items-start gap-2">
                                    <span className="mt-1 w-1.5 h-1.5 bg-pink-400 rounded-full flex-shrink-0" />
                                    Keep messages under 160 characters
                                </li>
                                <li className="flex items-start gap-2">
                                    <span className="mt-1 w-1.5 h-1.5 bg-pink-400 rounded-full flex-shrink-0" />
                                    Celebrate small wins frequently
                                </li>
                            </ul>
                        </div>
                        <div>
                            <h3 className="font-bold text-pink-800 mb-2 uppercase tracking-wide text-xs">Cultural Considerations</h3>
                            <ul className="space-y-2 text-pink-700">
                                <li className="flex items-start gap-2">
                                    <span className="mt-1 w-1.5 h-1.5 bg-pink-400 rounded-full flex-shrink-0" />
                                    Some cultures prefer formal address (Mr./Mrs.)
                                </li>
                                <li className="flex items-start gap-2">
                                    <span className="mt-1 w-1.5 h-1.5 bg-pink-400 rounded-full flex-shrink-0" />
                                    Respect timing of messages (e.g., prayer times)
                                </li>
                                <li className="flex items-start gap-2">
                                    <span className="mt-1 w-1.5 h-1.5 bg-pink-400 rounded-full flex-shrink-0" />
                                    Include both parents when appropriate
                                </li>
                                <li className="flex items-start gap-2">
                                    <span className="mt-1 w-1.5 h-1.5 bg-pink-400 rounded-full flex-shrink-0" />
                                    Recognize family vs. individual achievement
                                </li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
