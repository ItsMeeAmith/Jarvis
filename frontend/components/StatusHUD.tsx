"use client";

interface StatusHUDProps {
  status: "connecting" | "online" | "offline";
}

const STATUS_CONFIG = {
  online: { label: "JARVIS ONLINE", color: "var(--color-green)", dotClass: "pulse-green" },
  connecting: { label: "CONNECTING…", color: "#f0a500", dotClass: "" },
  offline: { label: "OFFLINE — RECONNECTING", color: "#ff4444", dotClass: "" },
};

export default function StatusHUD({ status }: StatusHUDProps) {
  const cfg = STATUS_CONFIG[status];

  return (
    <header
      className="flex items-center justify-between px-6 py-3 border-b"
      style={{
        borderColor: "var(--color-border)",
        background: "var(--color-surface)",
      }}
    >
      {/* Left: logo */}
      <span
        className="text-xs font-bold tracking-[0.3em] uppercase"
        style={{ color: "var(--color-cyan)" }}
      >
        J.A.R.V.I.S
      </span>

      {/* Center: status */}
      <div className="flex items-center gap-2">
        <span
          className={`w-2 h-2 rounded-full ${cfg.dotClass}`}
          style={{ background: cfg.color }}
        />
        <span
          className="text-xs font-semibold tracking-widest uppercase"
          style={{ color: cfg.color }}
        >
          {cfg.label}
        </span>
      </div>

      {/* Right: model tag */}
      <span
        className="text-xs tracking-widest uppercase"
        style={{ color: "var(--color-cyan-dim)" }}
      >
        llama-3.3-70b
      </span>
    </header>
  );
}
