import type { ReactNode } from "react";
import { cx } from "@/lib/utils";
import type { RiskLevel } from "@/data/types";

type BadgeTone = "critical" | "watch" | "healthy" | "info" | "teal" | "neutral";

const TONE_CLASSES: Record<BadgeTone, string> = {
  critical: "bg-red-light text-[#A3271F]",
  watch: "bg-amber-light text-[#8A5410]",
  healthy: "bg-green-light text-[#166B3A]",
  info: "bg-blue-light text-[#1D4CA8]",
  teal: "bg-teal-light text-[#0E6B63]",
  neutral: "bg-black/[0.05] text-text-mute",
};

export function Badge({ tone, children }: { tone: BadgeTone; children: ReactNode }) {
  return (
    <span
      className={cx(
        "inline-flex items-center rounded-pill px-2.5 py-0.5 text-[11px] font-semibold tracking-tight",
        TONE_CLASSES[tone]
      )}
    >
      {children}
    </span>
  );
}

export function RiskBadge({ level, risk }: { level?: RiskLevel; risk?: number }) {
  const resolved: RiskLevel = level ?? (risk! > 0.5 ? "critical" : risk! > 0.15 ? "watch" : "healthy");
  const label = resolved === "critical" ? "Critical" : resolved === "watch" ? "Watch" : "Healthy";
  const tone: BadgeTone = resolved === "critical" ? "critical" : resolved === "watch" ? "watch" : "healthy";
  return <Badge tone={tone}>{label}</Badge>;
}
