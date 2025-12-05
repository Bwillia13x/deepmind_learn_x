'use client';

import { BookOpen, Languages, Mic, FileText, Globe, AlertTriangle, GraduationCap, Users, BarChart3, Heart, Compass, MessageCircle, Sparkles, Zap, ArrowRight, Star, Clock, Globe2, WifiOff } from 'lucide-react';
import Link from 'next/link';

const coreFeatures = [
  {
    name: 'Text Leveler',
    description:
      'Paste any text and generate multiple readability levels with comprehension questions and bilingual glossaries.',
    href: '/leveler',
    icon: FileText,
    color: 'bg-blue-500',
  },
  {
    name: 'Decodable Generator',
    description:
      'Create phonics-constrained texts based on your scope and sequence for early readers.',
    href: '/decodable',
    icon: BookOpen,
    color: 'bg-green-500',
  },
  {
    name: 'Reading Buddy',
    description:
      'Practice reading fluency with instant feedback on words per minute and accuracy.',
    href: '/reading',
    icon: Mic,
    color: 'bg-teal-500',
  },
  {
    name: 'Live Captions',
    description:
      'Real-time speech-to-text with simplification and translation for classroom instruction.',
    href: '/captions',
    icon: Mic,
    color: 'bg-purple-500',
  },
  {
    name: 'Translation & Glossary',
    description:
      'Generate bilingual glossaries and translations for any content in 12+ languages.',
    href: '/glossary',
    icon: Languages,
    color: 'bg-orange-500',
  },
  {
    name: 'Analytics Dashboard',
    description:
      'Track student progress, identify struggling learners, and monitor class performance.',
    href: '/analytics',
    icon: BarChart3,
    color: 'bg-indigo-500',
  },
  {
    name: 'Offline Mode',
    description:
      'Access core features without an internet connection. Sync data when you reconnect.',
    href: '/offline',
    icon: WifiOff,
    color: 'bg-gray-500',
  },
];

const novelFeatures = [
  {
    name: 'L1 Transfer Intelligence',
    description:
      'Understand how each student\'s first language affects their English learning with targeted interventions.',
    href: '/l1-transfer',
    icon: Globe,
    color: 'bg-red-500',
    badge: 'NEW',
  },
  {
    name: 'Predictive Interventions',
    description:
      'Identify at-risk students 4-6 weeks early and generate prescriptive intervention plans.',
    href: '/interventions',
    icon: AlertTriangle,
    color: 'bg-amber-500',
    badge: 'NEW',
  },
  {
    name: 'Curriculum Mapping',
    description:
      'Map activities to Alberta ELA outcomes and ESL Proficiency Benchmarks automatically.',
    href: '/curriculum',
    icon: GraduationCap,
    color: 'bg-emerald-500',
    badge: 'NEW',
  },
  {
    name: 'Family Literacy',
    description:
      'Engage families with bilingual homework helpers, SMS lessons, and progress celebrations.',
    href: '/family',
    icon: Users,
    color: 'bg-pink-500',
    badge: 'NEW',
  },
  {
    name: 'SLIFE Pathways',
    description:
      'Age-appropriate, low-reading-level content for students with limited or interrupted formal education.',
    href: '/slife',
    icon: Compass,
    color: 'bg-purple-500',
    badge: 'NEW',
  },
  {
    name: 'Cultural Responsiveness',
    description:
      'Cultural context, communication norms, and teaching recommendations for diverse classrooms.',
    href: '/cultural',
    icon: Heart,
    color: 'bg-rose-500',
    badge: 'NEW',
  },
  {
    name: 'Class Orals Manager',
    description:
      'Run parallel small-group speaking tasks with AI monitoring accuracy, participation, and turn-taking.',
    href: '/orals',
    icon: MessageCircle,
    color: 'bg-cyan-500',
    badge: 'NEW',
  },
];

export default function Home() {
  return (
    <div className="space-y-12 pb-12">
      <div className="text-center space-y-4 py-8">
        <h1 className="text-5xl font-bold text-gray-900 tracking-tight">
          Welcome to <span className="text-indigo-600">Alberta ESL AI</span>
        </h1>
        <p className="text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed">
          AI-powered tools to support ESL teachers and students in Alberta
          schools. Create leveled content, generate decodables, and provide
          real-time language support.
        </p>
      </div>

      {/* Novel Alberta-Specific Features */}
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-3">
            <Sparkles className="w-6 h-6 text-indigo-600" />
            <span className="bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
              Alberta-Specific Features
            </span>
            <span className="text-xs bg-indigo-100 text-indigo-700 px-2.5 py-0.5 rounded-full font-bold border border-indigo-200 tracking-wide">NEW</span>
          </h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {novelFeatures.map((feature) => (
            <Link
              key={feature.name}
              href={feature.href}
              className="group bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-md hover:border-indigo-200 transition-all duration-200 relative overflow-hidden"
            >
              <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-br from-gray-50 to-transparent rounded-bl-full -mr-10 -mt-10 opacity-50 group-hover:opacity-100 transition-opacity" />

              <div className="flex items-start space-x-4 relative z-10">
                <div
                  className={`${feature.color} p-3 rounded-xl text-white shadow-sm group-hover:scale-110 group-hover:rotate-3 transition-transform duration-200`}
                >
                  <feature.icon className="w-6 h-6" />
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <h3 className="text-lg font-bold text-gray-900 group-hover:text-indigo-600 transition-colors">
                      {feature.name}
                    </h3>
                    {feature.badge && (
                      <span className="text-[10px] font-bold bg-indigo-600 text-white px-2 py-0.5 rounded-full shadow-sm">
                        {feature.badge}
                      </span>
                    )}
                  </div>
                  <p className="text-gray-600 text-sm leading-relaxed">{feature.description}</p>
                </div>
              </div>

              <div className="absolute bottom-4 right-4 opacity-0 group-hover:opacity-100 transition-opacity transform translate-x-2 group-hover:translate-x-0">
                <ArrowRight className="w-5 h-5 text-indigo-400" />
              </div>
            </Link>
          ))}
        </div>
      </div>

      {/* Core Features */}
      <div className="space-y-6">
        <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-3">
          <Zap className="w-6 h-6 text-amber-500" />
          Core Tools
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {coreFeatures.map((feature) => (
            <Link
              key={feature.name}
              href={feature.href}
              className="group bg-white rounded-xl shadow-sm border border-gray-200 p-5 hover:shadow-md hover:border-amber-200 transition-all duration-200"
            >
              <div className="flex flex-col h-full">
                <div className="flex items-start justify-between mb-4">
                  <div
                    className={`${feature.color} p-2.5 rounded-lg text-white shadow-sm group-hover:scale-110 transition-transform duration-200`}
                  >
                    <feature.icon className="w-5 h-5" />
                  </div>
                  <ArrowRight className="w-4 h-4 text-gray-300 group-hover:text-gray-500 transition-colors" />
                </div>

                <h3 className="text-base font-bold text-gray-900 group-hover:text-gray-700 transition-colors mb-2">
                  {feature.name}
                </h3>
                <p className="text-gray-500 text-sm leading-relaxed flex-1">{feature.description}</p>
              </div>
            </Link>
          ))}
        </div>
      </div>

      <div className="bg-gradient-to-br from-indigo-600 to-purple-700 rounded-2xl p-8 text-white shadow-lg overflow-hidden relative">
        <div className="absolute top-0 right-0 w-64 h-64 bg-white opacity-5 rounded-full -mr-20 -mt-20 blur-3xl" />
        <div className="absolute bottom-0 left-0 w-64 h-64 bg-white opacity-5 rounded-full -ml-20 -mb-20 blur-3xl" />

        <div className="relative z-10">
          <h2 className="text-2xl font-bold mb-8 flex items-center gap-3">
            <Star className="w-6 h-6 text-yellow-300 fill-yellow-300" />
            Quick Start Guide
          </h2>
          <div className="grid md:grid-cols-4 gap-8">
            {[
              { title: 'Text Leveler', desc: 'Paste content & select levels (A1-B2)', icon: FileText },
              { title: 'Choose L1', desc: 'Select student languages for glossaries', icon: Globe2 },
              { title: 'Generate', desc: 'Get adapted versions with support', icon: Zap },
              { title: 'Export', desc: 'Download for your classroom', icon: GraduationCap },
            ].map((step, i) => (
              <div key={i} className="relative group">
                <div className="flex flex-col items-center text-center">
                  <div className="w-14 h-14 bg-white/10 backdrop-blur-sm rounded-2xl flex items-center justify-center mb-4 border border-white/20 group-hover:bg-white/20 transition-colors">
                    <step.icon className="w-7 h-7 text-white" />
                  </div>
                  <h3 className="font-bold text-lg mb-2">{step.title}</h3>
                  <p className="text-sm text-indigo-100 leading-relaxed">{step.desc}</p>
                </div>
                {i < 3 && (
                  <div className="hidden md:block absolute top-7 left-1/2 w-full h-0.5 bg-white/20 -z-10 transform translate-x-1/2" />
                )}
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Key Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 text-center">
          <div className="text-4xl font-bold text-indigo-600 mb-1">13</div>
          <div className="text-sm font-medium text-gray-500">Languages Supported</div>
        </div>
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 text-center">
          <div className="text-4xl font-bold text-emerald-600 mb-1">K-9</div>
          <div className="text-sm font-medium text-gray-500">Grade Levels</div>
        </div>
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 text-center">
          <div className="text-4xl font-bold text-purple-600 mb-1">5</div>
          <div className="text-sm font-medium text-gray-500">ESL Benchmark Levels</div>
        </div>
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 text-center">
          <div className="text-4xl font-bold text-amber-600 mb-1">7h+</div>
          <div className="text-sm font-medium text-gray-500">Weekly Time Saved</div>
        </div>
      </div>
    </div>
  );
}
