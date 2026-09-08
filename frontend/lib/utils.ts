import type { Pump, RiskLevel } from "@/data/types";

export const CRIT = 0.5;
export const WARN = 0.15;

export function riskLevel(r: number): RiskLevel {
  return r > CRIT ? "critical" : r > WARN ? "watch" : "healthy";
}

export function riskWord(r: number): string {
  const level = riskLevel(r);
  return level === "critical" ? "Critical" : level === "watch" ? "Watch" : "Healthy";
}

export function riskColorVar(r: number): string {
  const level = riskLevel(r);
  return level === "critical" ? "var(--color-red)" : level === "watch" ? "var(--color-amber)" : "var(--color-green)";
}

export function pct(x: number): string {
  return (x * 100).toFixed(1) + "%";
}

export function days(h: number): string {
  return (h / 24).toFixed(1);
}

export function cx(...args: Array<string | false | null | undefined>): string {
  return args.filter(Boolean).join(" ");
}

export function sortByRiskDesc(list: Pump[]): Pump[] {
  return [...list].sort((a, b) => b.risk_probability - a.risk_probability);
}
