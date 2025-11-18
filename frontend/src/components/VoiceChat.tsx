import { useState, useRef, useEffect } from "react";
import { Button } from "./ui/button";
import { Mic, MicOff, Volume2, VolumeX, Loader2 } from "lucide-react";

interface VoiceChatProps {
  onClose?: () => void;
}

export function VoiceChat({ onClose }: VoiceChatProps) {
  const [isConnected, setIsConnected] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [status, setStatus] = useState<string>("Disconnected");
  const [error, setError] = useState<string | null>(null);

  const wsRef = useRef<WebSocket | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const audioChunksRef = useRef<ArrayBuffer[]>([]);
  const streamRef = useRef<MediaStream | null>(null);

  // Initialize WebSocket connection
  useEffect(() => {
    connectWebSocket();

    return () => {
      disconnect();
    };
  }, []);

  const connectWebSocket = () => {
    try {
      const ws = new WebSocket("ws://localhost:8000/api/v1/ws/voice-chat");
      wsRef.current = ws;

      ws.onopen = () => {
        setIsConnected(true);
        setStatus("Connected - Click microphone to start talking");
        setError(null);
        console.log("WebSocket connected");
      };

      ws.onmessage = async (event) => {
        const data = JSON.parse(event.data);
        console.log("Received message:", data.type);

        switch (data.type) {
          case "session_started":
            setStatus(data.message);
            break;

          case "audio_response":
            // Play audio response from Gemini
            await playAudio(data.audio);
            break;

          case "text_response":
            console.log("Text response:", data.text);
            break;

          case "turn_complete":
            setIsPlaying(false);
            setStatus("Response complete - You can speak again");
            break;

          case "error":
            setError(data.message);
            setStatus("Error occurred");
            break;
        }
      };

      ws.onerror = (error) => {
        console.error("WebSocket error:", error);
        setError("Connection error");
        setStatus("Connection error");
      };

      ws.onclose = () => {
        setIsConnected(false);
        setStatus("Disconnected");
        console.log("WebSocket disconnected");
      };
    } catch (err) {
      console.error("Failed to connect:", err);
      setError("Failed to connect to voice chat");
    }
  };

  const startRecording = async () => {
    try {
      // Request microphone access
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          channelCount: 1,
          sampleRate: 16000,
          echoCancellation: true,
          noiseSuppression: true,
        },
      });

      streamRef.current = stream;

      // Create MediaRecorder
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: "audio/webm",
      });

      mediaRecorderRef.current = mediaRecorder;

      // Handle audio data
      mediaRecorder.ondataavailable = async (event) => {
        if (event.data.size > 0 && wsRef.current?.readyState === WebSocket.OPEN) {
          // Convert blob to base64 and send to server
          const arrayBuffer = await event.data.arrayBuffer();
          const base64Audio = arrayBufferToBase64(arrayBuffer);

          wsRef.current.send(
            JSON.stringify({
              type: "audio_data",
              audio: base64Audio,
            })
          );
        }
      };

      // Start recording with chunks every 100ms
      mediaRecorder.start(100);
      setIsRecording(true);
      setStatus("Listening... Speak now");
      setError(null);
    } catch (err) {
      console.error("Failed to start recording:", err);
      setError("Failed to access microphone");
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);

      // Stop all tracks
      if (streamRef.current) {
        streamRef.current.getTracks().forEach((track) => track.stop());
      }

      // Notify server that user stopped speaking
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send(
          JSON.stringify({
            type: "audio_end",
          })
        );
      }

      setStatus("Processing... waiting for response");
    }
  };

  const playAudio = async (base64Audio: string) => {
    try {
      setIsPlaying(true);
      setStatus("Playing response...");

      // Decode base64 to ArrayBuffer
      const audioData = base64ToArrayBuffer(base64Audio);

      // Initialize AudioContext if not already done
      if (!audioContextRef.current) {
        audioContextRef.current = new AudioContext();
      }

      const audioContext = audioContextRef.current;

      // Decode and play audio
      const audioBuffer = await audioContext.decodeAudioData(audioData);
      const source = audioContext.createBufferSource();
      source.buffer = audioBuffer;
      source.connect(audioContext.destination);

      source.onended = () => {
        setIsPlaying(false);
        setStatus("Ready - Click microphone to speak");
      };

      source.start(0);
    } catch (err) {
      console.error("Failed to play audio:", err);
      setIsPlaying(false);
      setError("Failed to play audio response");
    }
  };

  const disconnect = () => {
    // Stop recording if active
    if (isRecording) {
      stopRecording();
    }

    // Close WebSocket
    if (wsRef.current) {
      wsRef.current.send(JSON.stringify({ type: "stop" }));
      wsRef.current.close();
      wsRef.current = null;
    }

    // Close AudioContext
    if (audioContextRef.current) {
      audioContextRef.current.close();
      audioContextRef.current = null;
    }

    setIsConnected(false);
    setIsRecording(false);
    setIsPlaying(false);
  };

  const toggleRecording = () => {
    if (isRecording) {
      stopRecording();
    } else {
      startRecording();
    }
  };

  // Helper functions
  const arrayBufferToBase64 = (buffer: ArrayBuffer): string => {
    const bytes = new Uint8Array(buffer);
    let binary = "";
    for (let i = 0; i < bytes.byteLength; i++) {
      binary += String.fromCharCode(bytes[i]);
    }
    return btoa(binary);
  };

  const base64ToArrayBuffer = (base64: string): ArrayBuffer => {
    const binaryString = atob(base64);
    const bytes = new Uint8Array(binaryString.length);
    for (let i = 0; i < binaryString.length; i++) {
      bytes[i] = binaryString.charCodeAt(i);
    }
    return bytes.buffer;
  };

  return (
    <div className="flex flex-col items-center justify-center h-full p-8 space-y-6">
      {/* Status Display */}
      <div className="text-center space-y-2">
        <div className="flex items-center justify-center space-x-2">
          <div
            className={`w-3 h-3 rounded-full ${
              isConnected ? "bg-green-500" : "bg-red-500"
            }`}
          />
          <span className="text-sm font-medium">
            {isConnected ? "Connected" : "Disconnected"}
          </span>
        </div>
        <p className="text-lg font-medium text-slate-700">{status}</p>
        {error && <p className="text-sm text-red-600">{error}</p>}
      </div>

      {/* Visual Indicator */}
      <div className="relative">
        <div
          className={`w-32 h-32 rounded-full flex items-center justify-center transition-all ${
            isRecording
              ? "bg-red-100 animate-pulse"
              : isPlaying
              ? "bg-blue-100 animate-pulse"
              : "bg-slate-100"
          }`}
        >
          {isPlaying ? (
            <Volume2 className="w-16 h-16 text-blue-600" />
          ) : isRecording ? (
            <Mic className="w-16 h-16 text-red-600" />
          ) : (
            <MicOff className="w-16 h-16 text-slate-400" />
          )}
        </div>

        {/* Pulse animation when recording */}
        {isRecording && (
          <div className="absolute inset-0 rounded-full bg-red-400 opacity-25 animate-ping" />
        )}
      </div>

      {/* Controls */}
      <div className="flex space-x-4">
        <Button
          onClick={toggleRecording}
          disabled={!isConnected || isPlaying}
          size="lg"
          variant={isRecording ? "destructive" : "default"}
          className="min-w-[140px]"
        >
          {isRecording ? (
            <>
              <MicOff className="w-5 h-5 mr-2" />
              Stop Talking
            </>
          ) : (
            <>
              <Mic className="w-5 h-5 mr-2" />
              Start Talking
            </>
          )}
        </Button>

        {!isConnected && (
          <Button onClick={connectWebSocket} size="lg" variant="outline">
            Reconnect
          </Button>
        )}
      </div>

      {/* Instructions */}
      <div className="mt-8 p-4 bg-blue-50 rounded-lg max-w-md">
        <h4 className="font-medium text-blue-900 mb-2">How to use:</h4>
        <ol className="text-sm text-blue-800 space-y-1 list-decimal list-inside">
          <li>Click "Start Talking" to begin recording</li>
          <li>Speak your question or message</li>
          <li>Click "Stop Talking" when finished</li>
          <li>Wait for the AI response to play</li>
        </ol>
      </div>
    </div>
  );
}
