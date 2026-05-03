"use client";

import { useEffect, useRef } from "react";
import type { Message } from "@/app/page";

interface ChatWindowProps {
  messages: Message[];
  isThinking: boolean;
}

export default function ChatWindow({ messages, isThinking }: ChatWindowProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isThinking]);

  return (
    <div className="flex-1 overflow-y-auto px-4 py-6 space-y-4">
      {messages.length === 0 && (
        <p className="text-center text-xs tracking-widest mt-20" style={{ color: "var(--color-cyan-dim)" }}>
          AWAITING YOUR COMMAND, SIR
        </p>
      )}

      {messages.map((msg) => (
        <div
          key={msg.id}
          className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
        >
          <div
            className="max-w-[75%] rounded px-4 py-2 text-sm leading-relaxed whitespace-pre-wrap"
            style={
              msg.role === "user"
                ? {
                    background: "rgba(0, 212, 255, 0.12)",
                    border: "1px solid var(--color-cyan)",
                    color: "var(--color-cyan)",
                  }
                : {
                    background: "rgba(255, 255, 255, 0.04)",
                    border: "1px solid var(--color-border)",
                    color: "#e0f4ff",
                  }
            }
          >
            {msg.role === "assistant" && (
              <span
                className="text-xs font-bold tracking-widest block mb-1"
                style={{ color: "var(--color-cyan-dim)" }}
              >
                JARVIS
              </span>
            )}
            {msg.content}
            {msg.streaming && (
              <span
                className="inline-block w-1.5 h-3 ml-0.5 align-middle"
                style={{ background: "var(--color-cyan)", animation: "pulse-green 0.8s infinite" }}
              />
            )}
          </div>
        </div>
      ))}

      {/* Typing indicator */}
      {isThinking && (
        <div className="flex justify-start">
          <div
            className="flex items-center gap-1 px-4 py-2 rounded"
            style={{
              background: "rgba(255, 255, 255, 0.04)",
              border: "1px solid var(--color-border)",
            }}
          >
            <span className="text-xs tracking-widest mr-2" style={{ color: "var(--color-cyan-dim)" }}>
              JARVIS
            </span>
            {[0, 1, 2].map((i) => (
              <span
                key={i}
                className="dot-bounce inline-block w-1.5 h-1.5 rounded-full"
                style={{ background: "var(--color-cyan)", animationDelay: `${i * 0.15}s` }}
              />
            ))}
          </div>
        </div>
      )}

      <div ref={bottomRef} />
    </div>
  );
}
