"use client";

import { useRef, useState } from "react";
import { Mic, MicOff, Loader2 } from "lucide-react";

type RecordingState = "idle" | "recording" | "processing";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

interface VoiceButtonProps {
  onTranscript: (text: string) => void;
  disabled?: boolean;
}

export default function VoiceButton({ onTranscript, disabled }: VoiceButtonProps) {
  const [state, setState] = useState<RecordingState>("idle");
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      mediaRecorderRef.current = recorder;
      chunksRef.current = [];

      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) chunksRef.current.push(e.data);
      };

      recorder.onstop = async () => {
        setState("processing");
        const blob = new Blob(chunksRef.current, { type: "audio/webm" });
        stream.getTracks().forEach((t) => t.stop());

        try {
          const formData = new FormData();
          formData.append("file", blob, "recording.webm");

          const response = await fetch(`${API_BASE}/voice/transcribe`, {
            method: "POST",
            body: formData,
          });

          if (!response.ok) throw new Error(`HTTP ${response.status}`);
          const data = await response.json();
          if (data.text) onTranscript(data.text.trim());
        } catch (err) {
          console.error("Transcription failed:", err);
        } finally {
          setState("idle");
        }
      };

      recorder.start();
      setState("recording");
    } catch (err) {
      console.error("Microphone access failed:", err);
      setState("idle");
    }
  };

  const stopRecording = () => {
    mediaRecorderRef.current?.stop();
  };

  const handleClick = () => {
    if (state === "idle") startRecording();
    else if (state === "recording") stopRecording();
  };

  const isRecording = state === "recording";
  const isProcessing = state === "processing";

  return (
    <button
      onClick={handleClick}
      disabled={disabled || isProcessing}
      title={isRecording ? "Stop recording" : "Start voice input"}
      className="flex items-center justify-center w-9 h-9 rounded-full transition-all disabled:opacity-30"
      style={{
        background: isRecording
          ? "rgba(255, 50, 50, 0.15)"
          : "rgba(0, 212, 255, 0.1)",
        border: `1px solid ${isRecording ? "#ff3232" : "var(--color-cyan)"}`,
      }}
    >
      {isProcessing ? (
        <Loader2
          size={16}
          className="animate-spin"
          style={{ color: "var(--color-cyan)" }}
        />
      ) : isRecording ? (
        <MicOff size={16} className="pulse-red" style={{ color: "#ff6666" }} />
      ) : (
        <Mic size={16} style={{ color: "var(--color-cyan)" }} />
      )}
    </button>
  );
}
