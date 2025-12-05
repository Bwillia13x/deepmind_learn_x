'use client';

import { useState } from 'react';
import { Globe, Users, Heart, Calendar, Utensils, BookOpen, MessageCircle, Search, AlertCircle, CheckCircle, ArrowRight } from 'lucide-react';

interface CultureInfo {
    code: string;
    name: string;
    region: string;
    languages: string[];
}

interface CulturalBrief {
    culture: CultureInfo;
    education?: {
        education_system: Record<string, string>;
        classroom_expectations: Record<string, string>;
        teaching_adaptations: string[];
    };
    communication?: {
        eye_contact: string;
        personal_space: string;
        authority_interaction: string;
        gender_dynamics: string;
        tips: string[];
    };
    family?: {
        structure: string;
        decision_making: string;
        extended_family_role: string;
        school_engagement_tips: string[];
    };
    celebrations?: Array<{
        name: string;
        timing: string;
        significance: string;
        school_implications: string;
    }>;
    dietary?: {
        restrictions: string[];
        fasting_periods: string[];
        school_lunch_notes: string;
    };
    teaching?: {
        do: string[];
        avoid: string[];
        conversation_starters: string[];
    };
}

// Demo cultural data for presentation
const DEMO_CULTURES: CultureInfo[] = [
    { code: 'somali', name: 'Somali', region: 'East Africa', languages: ['Somali', 'Arabic'] },
    { code: 'arabic', name: 'Arabic', region: 'Middle East / North Africa', languages: ['Arabic'] },
    { code: 'punjabi', name: 'Punjabi', region: 'South Asia', languages: ['Punjabi', 'Hindi', 'Urdu'] },
    { code: 'vietnamese', name: 'Vietnamese', region: 'Southeast Asia', languages: ['Vietnamese'] },
    { code: 'tagalog', name: 'Filipino', region: 'Southeast Asia', languages: ['Tagalog', 'English'] },
    { code: 'mandarin', name: 'Chinese', region: 'East Asia', languages: ['Mandarin', 'Cantonese'] },
    { code: 'korean', name: 'Korean', region: 'East Asia', languages: ['Korean'] },
    { code: 'farsi', name: 'Persian/Iranian', region: 'Middle East', languages: ['Farsi', 'Dari'] },
    { code: 'ukrainian', name: 'Ukrainian', region: 'Eastern Europe', languages: ['Ukrainian', 'Russian'] },
    { code: 'spanish', name: 'Latin American', region: 'Latin America', languages: ['Spanish'] },
];

const DEMO_BRIEF: Record<string, CulturalBrief> = {
    somali: {
        culture: { code: 'somali', name: 'Somali', region: 'East Africa', languages: ['Somali', 'Arabic'] },
        education: {
            education_system: {
                structure: 'Traditionally Quranic schools, formal education often interrupted',
                literacy: 'Somali script relatively new (1972); many older generations primarily oral'
            },
            classroom_expectations: {
                participation: 'May be quieter initially; respect for teacher authority',
                groupwork: 'Strong collaborative traditions within same-gender groups'
            },
            teaching_adaptations: [
                'Use oral and visual instruction alongside text',
                'Allow extra processing time for written tasks',
                'Build on strong memorization skills',
                'Consider gender dynamics for group work'
            ]
        },
        communication: {
            eye_contact: 'Direct eye contact with authority figures may be considered disrespectful',
            personal_space: 'Same-gender physical contact normal; cross-gender space expectations',
            authority_interaction: 'High respect for teachers; may not question or disagree openly',
            gender_dynamics: 'Gender roles typically more defined; awareness needed for co-ed activities',
            tips: [
                'Indirect communication style - read between the lines',
                'Initial quietness shows respect, not disengagement',
                'Family decisions often involve extended family elders'
            ]
        },
        family: {
            structure: 'Extended family paramount; clan connections important',
            decision_making: 'Often involves consultation with elders and extended family',
            extended_family_role: 'Uncles, aunts, grandparents have significant parenting role',
            school_engagement_tips: [
                'Welcome extended family members at conferences',
                'Consider phone/oral communication over written',
                'Father or uncle may be primary school contact'
            ]
        },
        celebrations: [
            {
                name: 'Eid al-Fitr',
                timing: 'End of Ramadan (varies)',
                significance: 'Major celebration marking end of fasting month',
                school_implications: 'Students may be absent; consider homework flexibility'
            },
            {
                name: 'Eid al-Adha',
                timing: 'During Hajj season (varies)',
                significance: 'Festival of Sacrifice - major religious holiday',
                school_implications: '2-3 day celebration; family gatherings'
            }
        ],
        dietary: {
            restrictions: ['Halal meat only', 'No pork or pork products', 'No alcohol in food'],
            fasting_periods: ['Ramadan - dawn to sunset fasting for 30 days'],
            school_lunch_notes: 'Check all ingredients; gelatin often contains pork'
        },
        teaching: {
            do: [
                'Acknowledge their resilience and strengths',
                'Learn a few Somali greetings',
                'Connect learning to oral traditions',
                'Provide visual supports and scaffolding'
            ],
            avoid: [
                'Assumptions about trauma (let students share when ready)',
                'Forcing eye contact as engagement indicator',
                'Scheduling major assessments during Ramadan',
                'Pairing students in mixed-gender groups without consideration'
            ],
            conversation_starters: [
                'Tell me about your family',
                'What languages do you speak at home?',
                'What do you enjoy learning about?'
            ]
        }
    },
    arabic: {
        culture: { code: 'arabic', name: 'Arabic', region: 'Middle East / North Africa', languages: ['Arabic'] },
        education: {
            education_system: {
                structure: 'Varies by country; often emphasizes memorization and respect',
                literacy: 'Arabic script reads right-to-left; strong literary tradition'
            },
            classroom_expectations: {
                participation: 'May wait to be called on; teacher-centered learning familiar',
                groupwork: 'Collaborative learning valued'
            },
            teaching_adaptations: [
                'Explicit instruction in left-to-right text directionality',
                'Build on strong memorization skills',
                'Use visual supports for abstract concepts',
                'Allow time to adjust to interactive learning styles'
            ]
        },
        communication: {
            eye_contact: 'May vary by gender and region',
            personal_space: 'Same-gender closeness common',
            authority_interaction: 'High respect for teachers and elders',
            gender_dynamics: 'Varies widely; be observant and respectful',
            tips: [
                'Hospitality is paramount - accept offered refreshments',
                'Avoid showing soles of feet or pointing',
                'Allow relationship building before direct questions'
            ]
        },
        family: {
            structure: 'Extended family centered; strong intergenerational bonds',
            decision_making: 'Consultation with elders common',
            extended_family_role: 'Grandparents often live with family',
            school_engagement_tips: [
                'Formal communication appreciated',
                'Consider involving extended family in decisions',
                'Phone calls may be preferred to emails'
            ]
        },
        celebrations: [
            {
                name: 'Eid al-Fitr',
                timing: 'End of Ramadan',
                significance: 'Breaking of fast celebration',
                school_implications: 'Major holiday; attendance flexibility needed'
            }
        ],
        dietary: {
            restrictions: ['Halal meat required', 'No pork', 'No alcohol'],
            fasting_periods: ['Ramadan'],
            school_lunch_notes: 'Halal options important'
        },
        teaching: {
            do: [
                'Show respect for their culture and religion',
                'Provide structured learning environments',
                'Use explicit phonics instruction for English sounds'
            ],
            avoid: [
                'Making generalizations about "Arab culture"',
                'Assuming political views',
                'Scheduling tests during religious holidays'
            ],
            conversation_starters: [
                'What country is your family from?',
                'Do you know how to write in Arabic?'
            ]
        }
    }
};

export default function CulturalResponsivenessPage() {
    const [activeTab, setActiveTab] = useState<'browse' | 'brief' | 'resources'>('browse');
    const [searchQuery, setSearchQuery] = useState('');
    const [brief, setBrief] = useState<CulturalBrief | null>(null);

    const filteredCultures = DEMO_CULTURES.filter(c =>
        c.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        c.region.toLowerCase().includes(searchQuery.toLowerCase()) ||
        c.languages.some(l => l.toLowerCase().includes(searchQuery.toLowerCase()))
    );

    const handleSelectCulture = async (code: string) => {
        try {
            const response = await fetch(
                `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/v1/cultural/brief`,
                {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        culture_code: code,
                        focus_areas: ['education', 'communication', 'family', 'celebrations', 'dietary', 'teaching']
                    })
                }
            );

            if (response.ok) {
                const data = await response.json();
                setBrief(data);
            } else {
                // Use demo data
                setBrief(DEMO_BRIEF[code] || DEMO_BRIEF.somali);
            }
        } catch {
            // Use demo data
            setBrief(DEMO_BRIEF[code] || DEMO_BRIEF.somali);
        } finally {
            setActiveTab('brief');
        }
    };

    return (
        <div className="min-h-screen bg-gray-50 p-8">
            <div className="max-w-7xl mx-auto space-y-8">
                {/* Header */}
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                    <div>
                        <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
                            <Globe className="w-8 h-8 text-rose-600" />
                            Cultural Responsiveness
                        </h1>
                        <p className="mt-2 text-gray-500">
                            Culturally responsive teaching resources for Alberta&apos;s diverse classrooms
                        </p>
                    </div>
                    <div className="bg-rose-50 text-rose-700 px-4 py-2 rounded-full text-sm font-bold border border-rose-100 shadow-sm">
                        Alberta-Specific
                    </div>
                </div>

                {/* Info Banner */}
                <div className="bg-white border border-rose-100 rounded-xl p-6 shadow-sm flex items-start gap-4">
                    <div className="p-2 bg-rose-50 rounded-lg">
                        <Heart className="w-5 h-5 text-rose-600" />
                    </div>
                    <div>
                        <h3 className="font-bold text-gray-900 mb-1">About This Tool</h3>
                        <p className="text-sm text-gray-600 leading-relaxed">
                            This resource provides cultural context to support respectful, responsive teaching.
                            Remember that every student is an individual—use this as a starting point for
                            understanding, not as definitive information about any student or family.
                        </p>
                    </div>
                </div>

                {/* Tabs */}
                <div className="flex gap-2 border-b border-gray-200">
                    <button
                        onClick={() => setActiveTab('browse')}
                        className={`px-6 py-3 font-bold text-sm transition-all border-b-2 ${activeTab === 'browse'
                                ? 'text-rose-600 border-rose-600'
                                : 'text-gray-500 border-transparent hover:text-gray-700'
                            }`}
                    >
                        <div className="flex items-center gap-2">
                            <Globe className="w-4 h-4" />
                            Browse Cultures
                        </div>
                    </button>
                    {brief && (
                        <button
                            onClick={() => setActiveTab('brief')}
                            className={`px-6 py-3 font-bold text-sm transition-all border-b-2 ${activeTab === 'brief'
                                    ? 'text-rose-600 border-rose-600'
                                    : 'text-gray-500 border-transparent hover:text-gray-700'
                                }`}
                        >
                            <div className="flex items-center gap-2">
                                <BookOpen className="w-4 h-4" />
                                Cultural Brief: {brief.culture.name}
                            </div>
                        </button>
                    )}
                </div>

                {/* Content */}
                {activeTab === 'browse' && (
                    <div className="space-y-6">
                        <div className="relative">
                            <input
                                type="text"
                                placeholder="Search cultures, regions, or languages..."
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                                className="w-full pl-12 pr-4 py-4 bg-white border border-gray-200 rounded-xl focus:ring-2 focus:ring-rose-500 focus:border-rose-500 outline-none shadow-sm transition-all"
                            />
                            <Search className="absolute left-4 top-4 text-gray-400 w-5 h-5" />
                        </div>

                        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                            {filteredCultures.map((culture) => (
                                <button
                                    key={culture.code}
                                    onClick={() => handleSelectCulture(culture.code)}
                                    className="bg-white p-6 rounded-xl border border-gray-200 hover:border-rose-300 hover:shadow-md transition-all text-left group"
                                >
                                    <div className="flex justify-between items-start mb-4">
                                        <h3 className="text-lg font-bold text-gray-900 group-hover:text-rose-600 transition-colors">
                                            {culture.name}
                                        </h3>
                                        <ArrowRight className="w-5 h-5 text-gray-300 group-hover:text-rose-500 transition-colors" />
                                    </div>
                                    <div className="space-y-2">
                                        <div className="text-sm text-gray-500 flex items-center gap-2">
                                            <Globe className="w-4 h-4" />
                                            {culture.region}
                                        </div>
                                        <div className="text-sm text-gray-500 flex items-center gap-2">
                                            <MessageCircle className="w-4 h-4" />
                                            {culture.languages.join(', ')}
                                        </div>
                                    </div>
                                </button>
                            ))}
                        </div>
                    </div>
                )}

                {activeTab === 'brief' && brief && (
                    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
                        {/* Brief Header */}
                        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-8">
                            <div className="flex items-center gap-4 mb-6">
                                <div className="w-16 h-16 bg-rose-100 rounded-full flex items-center justify-center text-2xl font-bold text-rose-600">
                                    {brief.culture.name.charAt(0)}
                                </div>
                                <div>
                                    <h2 className="text-2xl font-bold text-gray-900">{brief.culture.name} Culture Brief</h2>
                                    <p className="text-gray-500 flex items-center gap-2 mt-1">
                                        <Globe className="w-4 h-4" />
                                        {brief.culture.region} • {brief.culture.languages.join(', ')}
                                    </p>
                                </div>
                            </div>

                            <div className="grid md:grid-cols-2 gap-8">
                                {/* Education */}
                                <div className="space-y-4">
                                    <h3 className="font-bold text-gray-900 flex items-center gap-2 border-b border-gray-100 pb-2">
                                        <BookOpen className="w-5 h-5 text-indigo-600" />
                                        Education Context
                                    </h3>
                                    <div className="bg-indigo-50 rounded-xl p-5 border border-indigo-100 space-y-4">
                                        <div>
                                            <div className="text-xs font-bold text-indigo-400 uppercase tracking-wider mb-1">System Structure</div>
                                            <p className="text-sm text-gray-700">{brief.education?.education_system.structure}</p>
                                        </div>
                                        <div>
                                            <div className="text-xs font-bold text-indigo-400 uppercase tracking-wider mb-1">Classroom Expectations</div>
                                            <p className="text-sm text-gray-700">{brief.education?.classroom_expectations.participation}</p>
                                        </div>
                                    </div>
                                </div>

                                {/* Communication */}
                                <div className="space-y-4">
                                    <h3 className="font-bold text-gray-900 flex items-center gap-2 border-b border-gray-100 pb-2">
                                        <MessageCircle className="w-5 h-5 text-green-600" />
                                        Communication Style
                                    </h3>
                                    <div className="bg-green-50 rounded-xl p-5 border border-green-100 space-y-4">
                                        <div className="grid grid-cols-2 gap-4">
                                            <div>
                                                <div className="text-xs font-bold text-green-600 uppercase tracking-wider mb-1">Eye Contact</div>
                                                <p className="text-sm text-gray-700">{brief.communication?.eye_contact}</p>
                                            </div>
                                            <div>
                                                <div className="text-xs font-bold text-green-600 uppercase tracking-wider mb-1">Authority</div>
                                                <p className="text-sm text-gray-700">{brief.communication?.authority_interaction}</p>
                                            </div>
                                        </div>
                                        <div className="bg-white p-3 rounded-lg border border-green-100">
                                            <div className="text-xs font-bold text-green-600 uppercase tracking-wider mb-2">Key Tip</div>
                                            <p className="text-sm text-gray-600 italic">&quot;{brief.communication?.tips[0]}&quot;</p>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Teaching Strategies */}
                        <div className="grid md:grid-cols-2 gap-6">
                            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                                <h3 className="font-bold text-gray-900 mb-4 flex items-center gap-2">
                                    <CheckCircle className="w-5 h-5 text-green-600" />
                                    Recommended Practices
                                </h3>
                                <ul className="space-y-3">
                                    {brief.teaching?.do.map((item, i) => (
                                        <li key={i} className="flex items-start gap-3 text-sm text-gray-600">
                                            <div className="w-1.5 h-1.5 rounded-full bg-green-500 mt-1.5 flex-shrink-0" />
                                            {item}
                                        </li>
                                    ))}
                                </ul>
                            </div>

                            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                                <h3 className="font-bold text-gray-900 mb-4 flex items-center gap-2">
                                    <AlertCircle className="w-5 h-5 text-orange-600" />
                                    Practices to Avoid
                                </h3>
                                <ul className="space-y-3">
                                    {brief.teaching?.avoid.map((item, i) => (
                                        <li key={i} className="flex items-start gap-3 text-sm text-gray-600">
                                            <div className="w-1.5 h-1.5 rounded-full bg-orange-500 mt-1.5 flex-shrink-0" />
                                            {item}
                                        </li>
                                    ))}
                                </ul>
                            </div>
                        </div>

                        {/* Additional Info */}
                        <div className="grid md:grid-cols-3 gap-6">
                            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                                <h3 className="font-bold text-gray-900 mb-4 flex items-center gap-2">
                                    <Users className="w-5 h-5 text-blue-600" />
                                    Family Dynamics
                                </h3>
                                <p className="text-sm text-gray-600 mb-4">{brief.family?.structure}</p>
                                <div className="bg-blue-50 p-3 rounded-lg border border-blue-100">
                                    <div className="text-xs font-bold text-blue-600 uppercase tracking-wider mb-1">Engagement Tip</div>
                                    <p className="text-xs text-blue-800">{brief.family?.school_engagement_tips[0]}</p>
                                </div>
                            </div>

                            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                                <h3 className="font-bold text-gray-900 mb-4 flex items-center gap-2">
                                    <Calendar className="w-5 h-5 text-purple-600" />
                                    Key Celebrations
                                </h3>
                                <div className="space-y-4">
                                    {brief.celebrations?.map((cel, i) => (
                                        <div key={i}>
                                            <div className="font-bold text-sm text-gray-900">{cel.name}</div>
                                            <div className="text-xs text-gray-500 mb-1">{cel.timing}</div>
                                            <p className="text-xs text-gray-600">{cel.school_implications}</p>
                                        </div>
                                    ))}
                                </div>
                            </div>

                            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                                <h3 className="font-bold text-gray-900 mb-4 flex items-center gap-2">
                                    <Utensils className="w-5 h-5 text-orange-600" />
                                    Dietary Considerations
                                </h3>
                                <ul className="space-y-2 mb-4">
                                    {brief.dietary?.restrictions.map((item, i) => (
                                        <li key={i} className="text-sm text-gray-600 flex items-center gap-2">
                                            <div className="w-1 h-1 rounded-full bg-orange-400" />
                                            {item}
                                        </li>
                                    ))}
                                </ul>
                                <div className="bg-orange-50 p-3 rounded-lg border border-orange-100">
                                    <div className="text-xs font-bold text-orange-600 uppercase tracking-wider mb-1">Lunch Note</div>
                                    <p className="text-xs text-orange-800">{brief.dietary?.school_lunch_notes}</p>
                                </div>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
