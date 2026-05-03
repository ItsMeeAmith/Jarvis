"use client";

import { useEffect, useRef, useState, useCallback } from "react";
import ChatWindow from "@/components/ChatWindow";
import VoiceButton from "@/components/VoiceButton";
import StatusHUD from "@/components/StatusHUD";

export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  streaming?: boolean;
}

const WS_URL =
  (process.env.NEXT_PUBLIC_API_URL?.replace(/^http/, "ws") ?? "ws://localhost:8000") +
  "/ws/chat";

const RECONNECT_DELAY_MS = 3000;

export default function HomePage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [status, setStatus] = useState<"connecting" | "online" | "offline">("connecting");
  const [isThinking, setIsThinking] = useState(false);

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return;

    setStatus("connecting");
    const ws = new WebSocket(WS_URL);
    wsRef.current = ws;

    ws.onopen = () => setStatus("online");

    ws.onmessage = (event) => {
      const token: string = event.data;

      if (token === "[DONE]") {
        setIsThinking(false);
        setMessages((prev) =>
          prev.map((m) =>
            m.streaming ? { ...m, streaming: false } : m
          )
        );
        return;
      }

      if (token.startsWith("[ERROR]")) {
        setIsThinking(false);
        setMessages((prev) => [
          ...prev,
          {
            id: crypto.randomUUID(),
            role: "assistant",
            content: `⚠️ ${token.replace("[ERROR] ", "")}`,
          },
        ]);
        return;
      }

      setIsThinking(false);
      setMessages((prev) => {
        const last = prev[prev.length - 1];
        if (last?.streaming) {
          return [
            ...prev.slice(0, -1),
            { ...last, content: last.content + token },
          ];
        }
        return [
          ...prev,
          {
            id: crypto.randomUUID(),
            role: "assistant",
            content: token,
            streaming: true,
          },
        ];
      });
    };

    ws.onclose = () => {
      setStatus("offline");
      reconnectTimer.current = setTimeout(connect, RECONNECT_DELAY_MS);
    };

    ws.onerror = () => {
      ws.close();
    };
  }, []);

  useEffect(() => {
    connect();
    return () => {
      if (reconnectTimer.current) clearTimeout(reconnectTimer.current);
      wsRef.current?.close();
    };
  }, [connect]);

  const sendMessage = useCallback(() => {
    const text = input.trim();
    if (!text || wsRef.current?.readyState !== WebSocket.OPEN) return;

    setMessages((prev) => [
      ...prev,
      { id: crypto.randomUUID(), role: "user", content: text },
    ]);
    setInput("");
    setIsThinking(true);
    wsRef.current.send(text);
  }, [input]);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <main
      className="flex flex-col h-screen"
      style={{ background: "var(--color-bg)" }}
    >
      {/* Top HUD bar */}
      <StatusHUD status={status} />

      {/* Message list */}
      <ChatWindow messages={messages} isThinking={isThinking} />

      {/* Input bar */}
      <div
        className="flex items-center gap-3 px-4 py-3 border-t"
        style={{ borderColor: "var(--color-border)", background: "var(--color-surface)" }}
      >
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Speak your command, sir…"
          className="flex-1 bg-transparent outline-none text-sm placeholder-slate-500"
          style={{ color: "var(--color-cyan)" }}
          disabled={status !== "online" || isThinking}
        />
        <VoiceButton
          onTranscript={(text) => setInput((prev) => prev + text)}
          disabled={status !== "online" || isThinking}
        />
        <button
          onClick={sendMessage}
          disabled={status !== "online" || isThinking || !input.trim()}
          className="px-4 py-1.5 rounded text-xs font-bold uppercase tracking-widest disabled:opacity-30 transition-opacity"
          style={{
            background: "var(--color-cyan)",
            color: "var(--color-bg)",
          }}
        >
          Send
        </button>
      </div>
    </main>
  );
}
