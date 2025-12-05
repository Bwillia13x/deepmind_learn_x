'use client';

import { useEffect, useState, useRef, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';

interface SessionData {
    token: string;
    sessionId: number;
    participantId: number;
    nickname: string;
    l1: string;
}

interface GlossEntry {
    en: string;
    l1: string;
}

interface FocusCommand {
    verb: string;
    object: string;
}

interface CaptionSegment {
    id: number;
    text: string;
    simplified?: string;
    gloss?: GlossEntry[];
    focus?: FocusCommand[];
    timestamp: Date;
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const WS_URL = API_URL.replace('http', 'ws');

export default function CaptionsPage() {
    const router = useRouter();
    const [session, setSession] = useState<SessionData | null>(null);
    const [isConnected, setIsConnected] = useState(false);
    const [isRecording, setIsRecording] = useState(false);
    const [partialText, setPartialText] = useState('');
    const [segments, setSegments] = useState<CaptionSegment[]>([]);
    const [simplifyStrength, setSimplifyStrength] = useState(1);
    const [showL1, setShowL1] = useState(true);
    const [error, setError] = useState('');

    const wsRef = useRef<WebSocket | null>(null);
    const mediaStreamRef = useRef<MediaStream | null>(null);
    const audioContextRef = useRef<AudioContext | null>(null);
    const processorRef = useRef<ScriptProcessorNode | null>(null);
    const captionsEndRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        const stored = localStorage.getItem('session');
        if (!stored) {
            router.push('/');
            return;
        }
        setSession(JSON.parse(stored));
    }, [router]);

    // Auto-scroll to latest caption
    useEffect(() => {
        captionsEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [segments, partialText]);

    const connectWebSocket = useCallback(() => {
        if (wsRef.current?.readyState === WebSocket.OPEN) return;

        const ws = new WebSocket(`${WS_URL}/v1/captions/stream`);

        ws.onopen = () => {
            setIsConnected(true);
            setError('');
            // Send start message
            ws.send(JSON.stringify({
                type: 'start',
                sample_rate: 16000,
                lang: 'en',
                save: false,
                l1: session?.l1 || 'es',
                simplify: simplifyStrength,
                token: session?.token,
            }));
        };

        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);

            switch (data.type) {
                case 'ready':
                case 'started':
                    console.log('WebSocket ready');
                    break;
                case 'partial':
                    setPartialText(data.text || '');
                    break;
                case 'final':
                    setPartialText('');
                    setSegments(prev => [...prev, {
                        id: data.segment_id,
                        text: data.text,
                        simplified: data.simplified,
                        gloss: data.gloss,
                        focus: data.focus,
                        timestamp: new Date(),
                    }]);
                    break;
                case 'error':
                    setError(data.message);
                    break;
                case 'ping':
                    ws.send(JSON.stringify({ type: 'pong' }));
                    break;
            }
        };

        ws.onclose = () => {
            setIsConnected(false);
            setIsRecording(false);
        };

        ws.onerror = () => {
            setError('Connection error. Please try again.');
            setIsConnected(false);
        };

        wsRef.current = ws;
    }, [session, simplifyStrength]);

    const startRecording = async () => {
        try {
            // Connect WebSocket first
            connectWebSocket();

            // Get microphone access
            const stream = await navigator.mediaDevices.getUserMedia({
                audio: {
                    sampleRate: 16000,
                    channelCount: 1,
                    echoCancellation: true,
                    noiseSuppression: true,
                }
            });

            mediaStreamRef.current = stream;

            // Create audio context and processor
            const audioContext = new AudioContext({ sampleRate: 16000 });
            audioContextRef.current = audioContext;

            const source = audioContext.createMediaStreamSource(stream);
            const processor = audioContext.createScriptProcessor(4096, 1, 1);
            processorRef.current = processor;

            processor.onaudioprocess = (e) => {
                if (wsRef.current?.readyState === WebSocket.OPEN) {
                    const inputData = e.inputBuffer.getChannelData(0);
                    // Convert float32 to int16 PCM
                    const pcmData = new Int16Array(inputData.length);
                    for (let i = 0; i < inputData.length; i++) {
                        const s = Math.max(-1, Math.min(1, inputData[i]));
                        pcmData[i] = s < 0 ? s * 0x8000 : s * 0x7FFF;
                    }
                    wsRef.current.send(pcmData.buffer);
                }
            };

            source.connect(processor);
            processor.connect(audioContext.destination);

            setIsRecording(true);
            setError('');
        } catch (_err) {
            setError('Could not access microphone. Please allow microphone access.');
        }
    };

    const stopRecording = () => {
        // Stop audio processing
        if (processorRef.current) {
            processorRef.current.disconnect();
            processorRef.current = null;
        }
        if (audioContextRef.current) {
            audioContextRef.current.close();
            audioContextRef.current = null;
        }
        if (mediaStreamRef.current) {
            mediaStreamRef.current.getTracks().forEach(track => track.stop());
            mediaStreamRef.current = null;
        }

        // Send stop message and close WebSocket
        if (wsRef.current?.readyState === WebSocket.OPEN) {
            wsRef.current.send(JSON.stringify({ type: 'stop' }));
            wsRef.current.close();
        }

        setIsRecording(false);
        setIsConnected(false);
    };

    const clearCaptions = () => {
        setSegments([]);
        setPartialText('');
    };

    const speakText = (text: string) => {
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = 'en-US';
        utterance.rate = 0.8;
        speechSynthesis.speak(utterance);
    };

    if (!session) {
        return (
            <div className="min-h-screen flex items-center justify-center">
                <div className="animate-pulse text-2xl">Loading...</div>
            </div>
        );
    }

    return (
        <main className="min-h-screen flex flex-col bg-gray-50">
            {/* Header */}
            <header className="bg-white shadow-sm p-4 flex items-center justify-between sticky top-0 z-10 backdrop-blur-sm bg-white/90">
                <Link
                    href="/dashboard"
                    className="btn bg-gray-100 hover:bg-gray-200 text-gray-600"
                >
                    ⬅️ Back
                </Link>
                <h1 className="text-xl font-black text-blue-600">Live Captions 🎤</h1>
                <div className="flex items-center gap-2">
                    <div className={`w-3 h-3 rounded-full ${isConnected ? 'bg-green-500 animate-pulse' : 'bg-gray-300'}`} />
                    <span className="text-sm font-bold text-gray-600">
                        {isConnected ? 'Live' : 'Offline'}
                    </span>
                </div>
            </header>

            {/* Controls Bar */}
            <div className="bg-white border-b p-4 space-y-4 shadow-sm z-10">
                {error && (
                    <div className="bg-red-50 text-red-600 p-3 rounded-xl text-center font-bold border border-red-100">
                        {error}
                    </div>
                )}

                <div className="flex flex-col sm:flex-row gap-4">
                    {/* Simplify Slider */}
                    <div className="flex-1 bg-gray-50 p-3 rounded-xl flex items-center gap-4">
                        <label htmlFor="simplify-slider" className="text-sm font-bold text-gray-700 whitespace-nowrap">
                            Simplify Text:
                        </label>
                        <input
                            id="simplify-slider"
                            type="range"
                            min="0"
                            max="3"
                            value={simplifyStrength}
                            onChange={(e) => setSimplifyStrength(parseInt(e.target.value))}
                            className="flex-1 h-3 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-blue-500"
                            disabled={isRecording}
                            title="Adjust text simplification level"
                        />
                        <span className="text-xs font-black bg-white px-2 py-1 rounded-lg shadow-sm border border-gray-100 min-w-[60px] text-center">
                            {['OFF', 'EASY', 'MED', 'MAX'][simplifyStrength]}
                        </span>
                    </div>

                    {/* L1 Toggle */}
                    <button
                        onClick={() => setShowL1(!showL1)}
                        className={`px-4 py-3 rounded-xl font-bold transition-all flex items-center justify-center gap-2 shadow-sm ${showL1
                            ? 'bg-blue-500 text-white shadow-blue-200'
                            : 'bg-gray-100 text-gray-500'
                            }`}
                    >
                        <span>🌍</span>
                        <span>Translations {showL1 ? 'ON' : 'OFF'}</span>
                    </button>
                </div>
            </div>

            {/* Captions Area */}
            <div className="flex-1 overflow-y-auto p-4 space-y-6 bg-slate-50">
                {segments.length === 0 && !partialText && (
                    <div className="text-center text-gray-400 py-20 flex flex-col items-center">
                        <div className="text-8xl mb-6 opacity-50">🎤</div>
                        <p className="text-2xl font-black text-gray-300">Ready to Listen</p>
                        <p className="text-gray-400 mt-2">Press the green button to start</p>
                    </div>
                )}

                {segments.map((segment) => (
                    <div
                        key={segment.id}
                        className="card p-6 animate-fadeIn border-l-8 border-l-blue-500"
                    >
                        {/* Original text */}
                        <p className="text-2xl leading-relaxed text-gray-800 font-medium">
                            {segment.text}
                        </p>

                        {/* Simplified version */}
                        {segment.simplified && simplifyStrength > 0 && (
                            <div className="mt-4 p-4 bg-green-50 rounded-xl border border-green-100">
                                <p className="text-xs font-black text-green-600 uppercase tracking-wider mb-1">
                                    ✨ Simplified
                                </p>
                                <p className="text-xl text-green-800 font-medium">
                                    {segment.simplified}
                                </p>
                            </div>
                        )}

                        {/* Focus commands */}
                        {segment.focus && segment.focus.length > 0 && (
                            <div className="mt-4 flex flex-wrap gap-2">
                                {segment.focus.map((cmd, idx) => (
                                    <span
                                        key={idx}
                                        className="px-4 py-2 bg-yellow-100 text-yellow-800 rounded-xl text-sm font-bold border border-yellow-200 shadow-sm"
                                    >
                                        📌 {cmd.verb} {cmd.object}
                                    </span>
                                ))}
                            </div>
                        )}

                        {/* L1 Glossary */}
                        {showL1 && segment.gloss && segment.gloss.length > 0 && (
                            <div className="mt-4 p-4 bg-blue-50 rounded-xl border border-blue-100">
                                <p className="text-xs font-black text-blue-600 uppercase tracking-wider mb-2">
                                    📚 Key Words
                                </p>
                                <div className="flex flex-wrap gap-2">
                                    {segment.gloss.map((entry, idx) => (
                                        <button
                                            key={idx}
                                            onClick={() => speakText(entry.en)}
                                            className="px-3 py-2 bg-white rounded-lg shadow-sm text-base hover:bg-blue-50 transition-colors border border-blue-100 flex items-center gap-2"
                                        >
                                            <span className="font-bold text-gray-700">{entry.en}</span>
                                            <span className="text-gray-300">→</span>
                                            <span className="text-blue-600 font-bold">{entry.l1}</span>
                                            <span className="text-xs opacity-50">🔊</span>
                                        </button>
                                    ))}
                                </div>
                            </div>
                        )}
                    </div>
                ))}

                {/* Partial (live) text */}
                {partialText && (
                    <div className="bg-white/50 rounded-2xl p-6 animate-pulse border-2 border-dashed border-gray-300">
                        <p className="text-2xl text-gray-400 italic font-medium">
                            {partialText}...
                        </p>
                    </div>
                )}

                <div ref={captionsEndRef} />
            </div>

            {/* Bottom Controls */}
            <div className="bg-white border-t p-6 flex items-center justify-center gap-4 shadow-[0_-4px_6px_-1px_rgba(0,0,0,0.05)] z-20">
                {!isRecording ? (
                    <button
                        onClick={startRecording}
                        className="btn bg-green-500 hover:bg-green-600 text-white
                               text-xl font-black py-4 px-12 rounded-full
                               shadow-green-200 hover:shadow-green-300
                               transform hover:scale-105 flex items-center gap-3"
                    >
                        <span>🎤</span>
                        <span>Start Listening</span>
                    </button>
                ) : (
                    <button
                        onClick={stopRecording}
                        className="btn bg-red-500 hover:bg-red-600 text-white
                               text-xl font-black py-4 px-12 rounded-full
                               shadow-red-200 hover:shadow-red-300
                               transform hover:scale-105 flex items-center gap-3 animate-pulse"
                    >
                        <span>⏹️</span>
                        <span>Stop</span>
                    </button>
                )}

                {segments.length > 0 && (
                    <button
                        onClick={clearCaptions}
                        className="btn bg-gray-100 hover:bg-gray-200 text-gray-600
                               py-4 px-6 rounded-full font-bold"
                    >
                        Clear
                    </button>
                )}
            </div>
        </main>
    );
}
