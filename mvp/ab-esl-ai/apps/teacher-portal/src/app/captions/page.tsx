"use client";

import { useState, useRef, useEffect } from "react";

const WS_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000';

const MAX_RECONNECT_ATTEMPTS = 3;
const RECONNECT_DELAY = 2000;

interface Caption {
  text: string;
  simplified?: string;
  focus?: { verb: string; object: string }[];
  is_final: boolean;
  timestamp: number;
}

export default function CaptionsPage() {
  const [isConnected, setIsConnected] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [captions, setCaptions] = useState<Caption[]>([]);
  const [simplifyStrength, setSimplifyStrength] = useState(2);
  const [enableL1, setEnableL1] = useState(false);
  const [l1Language, setL1Language] = useState("es");
  const [error, setError] = useState("");
  const [reconnectAttempts, setReconnectAttempts] = useState(0);

  const wsRef = useRef<WebSocket | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  const languages = [
    { code: "ar", name: "Arabic" },
    { code: "es", name: "Spanish" },
    { code: "zh", name: "Chinese" },
    { code: "fr", name: "French" },
  ];

  const attemptReconnect = () => {
    if (reconnectAttempts < MAX_RECONNECT_ATTEMPTS) {
      setError(`Connection lost. Reconnecting... (${reconnectAttempts + 1}/${MAX_RECONNECT_ATTEMPTS})`);
      reconnectTimeoutRef.current = setTimeout(() => {
        setReconnectAttempts(prev => prev + 1);
        connectWebSocket();
      }, RECONNECT_DELAY);
    } else {
      setError("Connection lost. Please click Connect to try again.");
      setReconnectAttempts(0);
    }
  };

  const connectWebSocket = () => {
    try {
      const ws = new WebSocket(
        `${WS_URL}/v1/captions/stream?simplify_strength=${simplifyStrength}&l1=${l1Language}`
      );

      ws.onopen = () => {
        console.log("WebSocket connected");
        setIsConnected(true);
        setError("");
        setReconnectAttempts(0);
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);

          const newCaption: Caption = {
            text: data.text || "",
            simplified: data.simplified,
            focus: data.focus || [],
            is_final: data.is_final || false,
            timestamp: Date.now(),
          };

          setCaptions((prev) => {
            // Replace last partial with final, or add new
            if (newCaption.is_final && prev.length > 0 && !prev[prev.length - 1].is_final) {
              return [...prev.slice(0, -1), newCaption];
            }
            return [...prev, newCaption];
          });
        } catch (err) {
          console.error("Failed to parse message:", err);
        }
      };

      ws.onerror = (error) => {
        console.error("WebSocket error:", error);
        setIsConnected(false);
      };

      ws.onclose = (event) => {
        console.log("WebSocket disconnected", event.code);
        setIsConnected(false);
        // Auto-reconnect if it wasn't a clean close
        if (event.code !== 1000 && isRecording) {
          attemptReconnect();
        }
      };

      wsRef.current = ws;
    } catch (err: any) {
      setError(err.message || "Failed to connect");
    }
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          channelCount: 1,
          sampleRate: 16000,
        }
      });

      // Create AudioContext for processing
      const audioContext = new AudioContext({ sampleRate: 16000 });
      audioContextRef.current = audioContext;

      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm',
      });

      mediaRecorder.ondataavailable = async (event) => {
        if (event.data.size > 0 && wsRef.current?.readyState === WebSocket.OPEN) {
          // Send raw audio data to WebSocket
          const arrayBuffer = await event.data.arrayBuffer();
          wsRef.current.send(arrayBuffer);
        }
      };

      // Send audio chunks every 100ms
      mediaRecorder.start(100);
      mediaRecorderRef.current = mediaRecorder;
      setIsRecording(true);
      setError("");
    } catch (err: any) {
      setError(err.message || "Failed to access microphone");
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current) {
      mediaRecorderRef.current.stop();
      mediaRecorderRef.current.stream.getTracks().forEach(track => track.stop());
      mediaRecorderRef.current = null;
    }
    if (audioContextRef.current) {
      audioContextRef.current.close();
      audioContextRef.current = null;
    }
    setIsRecording(false);
  };

  const disconnectWebSocket = () => {
    // Clear any pending reconnection attempt
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
    setReconnectAttempts(0);

    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    stopRecording();
    setIsConnected(false);
  };

  const clearCaptions = () => {
    setCaptions([]);
  };

  useEffect(() => {
    return () => {
      disconnectWebSocket();
    };
  }, []);

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Live Captions</h1>
          <p className="text-gray-500 mt-2">
            Real-time speech-to-text with intelligent simplification and focus highlighting.
          </p>
        </div>

        {/* Controls */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
            {/* Simplification Strength */}
            <div>
              <label htmlFor="simplify-strength" className="block text-sm font-medium text-gray-700 mb-2">
                Simplification Level: {simplifyStrength}
              </label>
              <input
                id="simplify-strength"
                type="range"
                min="0"
                max="3"
                value={simplifyStrength}
                onChange={(e) => setSimplifyStrength(Number(e.target.value))}
                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-indigo-600"
                disabled={isConnected}
                aria-label="Simplification level slider"
              />
              <div className="flex justify-between text-xs text-gray-500 mt-1">
                <span>Off</span>
                <span>Medium</span>
                <span>High</span>
              </div>
            </div>

            {/* L1 Language */}
            <div>
              <label htmlFor="l1-language" className="block text-sm font-medium text-gray-700 mb-2">
                Translation Language
              </label>
              <select
                id="l1-language"
                value={l1Language}
                onChange={(e) => setL1Language(e.target.value)}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none transition-all"
                disabled={isConnected}
                aria-label="Select translation language"
              >
                {languages.map((lang) => (
                  <option key={lang.code} value={lang.code}>
                    {lang.name}
                  </option>
                ))}
              </select>
            </div>

            {/* Enable L1 */}
            <div className="flex items-end pb-2">
              <label className="flex items-center space-x-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={enableL1}
                  onChange={(e) => setEnableL1(e.target.checked)}
                  className="w-5 h-5 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500"
                />
                <span className="text-sm font-medium text-gray-700">
                  Enable Translation
                </span>
              </label>
            </div>
          </div>

          {/* Connection Controls */}
          <div className="flex flex-wrap gap-3">
            {!isConnected ? (
              <button
                onClick={connectWebSocket}
                className="px-6 py-2.5 bg-indigo-600 text-white font-medium rounded-lg hover:bg-indigo-700 transition-colors shadow-sm"
              >
                Connect
              </button>
            ) : (
              <>
                {!isRecording ? (
                  <button
                    onClick={startRecording}
                    className="px-6 py-2.5 bg-green-600 text-white font-medium rounded-lg hover:bg-green-700 transition-colors shadow-sm flex items-center gap-2"
                  >
                    <span>🎤</span> Start Recording
                  </button>
                ) : (
                  <button
                    onClick={stopRecording}
                    className="px-6 py-2.5 bg-red-600 text-white font-medium rounded-lg hover:bg-red-700 transition-colors shadow-sm animate-pulse flex items-center gap-2"
                  >
                    <span>⏹</span> Stop Recording
                  </button>
                )}
                <button
                  onClick={disconnectWebSocket}
                  className="px-6 py-2.5 bg-white border border-gray-300 text-gray-700 font-medium rounded-lg hover:bg-gray-50 transition-colors shadow-sm"
                >
                  Disconnect
                </button>
                <button
                  onClick={clearCaptions}
                  className="px-6 py-2.5 bg-white border border-gray-300 text-gray-700 font-medium rounded-lg hover:bg-gray-50 transition-colors shadow-sm"
                >
                  Clear
                </button>
              </>
            )}
          </div>

          {/* Status Indicator */}
          <div className="mt-6 flex items-center gap-2 pt-4 border-t border-gray-100">
            <div
              className={`w-2.5 h-2.5 rounded-full ${isConnected ? "bg-green-500" : "bg-gray-400"}`}
            />
            <span className="text-sm text-gray-600 font-medium">
              {isConnected
                ? isRecording
                  ? "Recording active"
                  : "Connected (ready)"
                : "Disconnected"}
            </span>
          </div>

          {error && (
            <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
              {error}
            </div>
          )}
        </div>

        {/* Captions Display */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 min-h-[400px]">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-lg font-bold text-gray-900">
              Transcript <span className="text-gray-400 font-normal text-sm ml-2">({captions.filter((c) => c.is_final).length} segments)</span>
            </h2>
          </div>

          <div className="space-y-4 max-h-[600px] overflow-y-auto pr-2 custom-scrollbar">
            {captions.length === 0 ? (
              <div className="text-center py-20">
                <div className="text-4xl mb-4 opacity-20">💬</div>
                <p className="text-gray-500">No captions yet.</p>
                <p className="text-sm text-gray-400 mt-1">Connect and start recording to see live transcription.</p>
              </div>
            ) : (
              captions.map((caption, idx) => (
                <div
                  key={idx}
                  className={`p-4 rounded-lg border-l-4 transition-all ${caption.is_final
                    ? "bg-gray-50 border-green-500"
                    : "bg-indigo-50 border-indigo-400 opacity-90"
                    }`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <p className="text-lg text-gray-900 mb-2 leading-relaxed">{caption.text}</p>

                      {caption.simplified && simplifyStrength > 0 && (
                        <div className="mt-3 p-3 bg-yellow-50 rounded-lg border border-yellow-100">
                          <p className="text-xs font-bold text-yellow-700 uppercase tracking-wide mb-1">
                            Simplified
                          </p>
                          <p className="text-gray-800">{caption.simplified}</p>
                        </div>
                      )}

                      {caption.focus && caption.focus.length > 0 && (
                        <div className="mt-3 flex flex-wrap gap-2">
                          {caption.focus.map((f, fIdx) => (
                            <span
                              key={fIdx}
                              className="px-2.5 py-1 bg-purple-100 text-purple-700 rounded-md text-sm font-medium border border-purple-200"
                            >
                              {f.verb} → {f.object}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>

                    <span className="text-xs text-gray-400 ml-4 font-mono">
                      {caption.is_final ? "FINAL" : "..."}
                    </span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Info Panel */}
        <div className="mt-8 bg-indigo-50 border border-indigo-100 rounded-xl p-6">
          <h3 className="font-bold text-indigo-900 mb-3 flex items-center gap-2">
            <span>💡</span> How it works
          </h3>
          <ul className="text-sm text-indigo-800 space-y-2 ml-1">
            <li className="flex items-start gap-2">
              <span className="mt-1">•</span>
              <span>Click <strong>Connect</strong> to establish a secure WebSocket connection to the server.</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="mt-1">•</span>
              <span>Click <strong>Start Recording</strong> to begin capturing audio from your microphone.</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="mt-1">•</span>
              <span>Speak clearly — captions will appear in real-time. Gray text indicates partial results, while green borders indicate finalized sentences.</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="mt-1">•</span>
              <span>Adjust the <strong>Simplification Level</strong> before connecting to control how much the AI simplifies complex language.</span>
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
}
