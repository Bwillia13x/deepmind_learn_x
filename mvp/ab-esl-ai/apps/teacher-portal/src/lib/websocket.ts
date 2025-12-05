export interface CaptionSegment {
  type: 'partial' | 'final';
  text: string;
  simplified?: string;
  words?: { w: string; s: number; e: number }[];
  focus?: { verb: string; object?: string }[];
  gloss?: { en: string; l1: string }[];
  segment_id?: number;
}

export type ConnectionStatus = 'disconnected' | 'connecting' | 'connected' | 'ready' | 'streaming' | 'recording' | 'error';

export class CaptionWebSocket {
  private ws: WebSocket | null = null;
  private audioContext: AudioContext | null = null;
  private mediaStream: MediaStream | null = null;
  private processor: ScriptProcessorNode | null = null;
  private source: MediaStreamAudioSourceNode | null = null;

  constructor(
    private onSegment: (segment: CaptionSegment) => void,
    private onStatus: (status: ConnectionStatus) => void,
    private onError: (error: string) => void
  ) { }

  async connect(options: {
    sampleRate?: number;
    lang?: string;
    simplify?: number;
    l1?: string;
    save?: boolean;
    token?: string;
  } = {}) {
    this.onStatus('connecting');

    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsHost = process.env.NEXT_PUBLIC_WS_HOST || window.location.host;
    const wsUrl = `${wsProtocol}//${wsHost}/api/v1/captions/stream`;

    try {
      this.ws = new WebSocket(wsUrl);
    } catch (_err) {
      this.onError('Failed to create WebSocket connection');
      this.onStatus('error');
      return;
    }

    this.ws.onopen = () => {
      this.onStatus('connected');
    };

    this.ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);

        if (data.type === 'ready') {
          this.onStatus('ready');
          // Send start message
          this.ws?.send(
            JSON.stringify({
              type: 'start',
              sample_rate: options.sampleRate || 16000,
              lang: options.lang || 'en',
              simplify: options.simplify || 0,
              l1: options.l1,
              save: options.save || false,
              token: options.token,
            })
          );
        } else if (data.type === 'started') {
          this.onStatus('streaming');
        } else if (data.type === 'partial' || data.type === 'final') {
          this.onSegment(data);
        } else if (data.type === 'error') {
          this.onError(data.message);
        } else if (data.type === 'ping') {
          this.ws?.send(JSON.stringify({ type: 'pong' }));
        }
      } catch (err) {
        console.error('Failed to parse WebSocket message:', err);
      }
    };

    this.ws.onerror = () => {
      this.onError('WebSocket connection error');
      this.onStatus('error');
    };

    this.ws.onclose = () => {
      this.onStatus('disconnected');
    };
  }

  async startRecording() {
    try {
      this.mediaStream = await navigator.mediaDevices.getUserMedia({
        audio: {
          sampleRate: 16000,
          channelCount: 1,
          echoCancellation: true,
          noiseSuppression: true,
        },
      });

      this.audioContext = new AudioContext({ sampleRate: 16000 });
      this.source = this.audioContext.createMediaStreamSource(this.mediaStream);
      this.processor = this.audioContext.createScriptProcessor(4096, 1, 1);

      this.processor.onaudioprocess = (e) => {
        if (this.ws?.readyState === WebSocket.OPEN) {
          const inputData = e.inputBuffer.getChannelData(0);
          const pcm16 = new Int16Array(inputData.length);
          for (let i = 0; i < inputData.length; i++) {
            pcm16[i] = Math.max(-32768, Math.min(32767, inputData[i] * 32768));
          }
          this.ws.send(pcm16.buffer);
        }
      };

      this.source.connect(this.processor);
      this.processor.connect(this.audioContext.destination);
      this.onStatus('recording');
    } catch (err) {
      if (err instanceof Error) {
        if (err.name === 'NotAllowedError') {
          this.onError('Microphone access denied. Please allow microphone access.');
        } else if (err.name === 'NotFoundError') {
          this.onError('No microphone found. Please connect a microphone.');
        } else {
          this.onError(`Microphone error: ${err.message}`);
        }
      } else {
        this.onError('Failed to access microphone');
      }
      this.onStatus('error');
    }
  }

  stopRecording() {
    if (this.processor) {
      this.processor.disconnect();
      this.processor = null;
    }
    if (this.source) {
      this.source.disconnect();
      this.source = null;
    }
    if (this.audioContext) {
      this.audioContext.close();
      this.audioContext = null;
    }
    if (this.mediaStream) {
      this.mediaStream.getTracks().forEach((track) => track.stop());
      this.mediaStream = null;
    }
  }

  disconnect() {
    this.stopRecording();
    if (this.ws) {
      try {
        this.ws.send(JSON.stringify({ type: 'stop' }));
      } catch {
        // Ignore send errors on disconnect
      }
      this.ws.close();
      this.ws = null;
    }
    this.onStatus('disconnected');
  }

  isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }
}
