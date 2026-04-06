import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatCurrency(value: number | null | undefined): string {
  if (value == null) return "N/A";
  if (Math.abs(value) >= 1e12) return `$${(value / 1e12).toFixed(1)}T`;
  if (Math.abs(value) >= 1e9) return `$${(value / 1e9).toFixed(1)}B`;
  if (Math.abs(value) >= 1e6) return `$${(value / 1e6).toFixed(0)}M`;
  if (Math.abs(value) >= 1e3) return `$${(value / 1e3).toFixed(0)}K`;
  return `$${value.toFixed(2)}`;
}

export function formatPercent(value: number | null | undefined): string {
  if (value == null) return "N/A";
  return `${value >= 0 ? "+" : ""}${value.toFixed(2)}%`;
}

export function formatNumber(value: number | null | undefined): string {
  if (value == null) return "N/A";
  return value.toLocaleString();
}

export function getScoreColor(score: number): string {
  if (score >= 80) return "text-emerald-400";
  if (score >= 60) return "text-green-400";
  if (score >= 40) return "text-yellow-400";
  if (score >= 20) return "text-orange-400";
  return "text-red-400";
}

export function getScoreBgColor(score: number): string {
  if (score >= 80) return "bg-emerald-400/20 border-emerald-400/50";
  if (score >= 60) return "bg-green-400/20 border-green-400/50";
  if (score >= 40) return "bg-yellow-400/20 border-yellow-400/50";
  if (score >= 20) return "bg-orange-400/20 border-orange-400/50";
  return "bg-red-400/20 border-red-400/50";
}

export function getSentimentColor(label: string): string {
  switch (label) {
    case "positive": return "text-emerald-400";
    case "negative": return "text-red-400";
    default: return "text-gray-400";
  }
}
