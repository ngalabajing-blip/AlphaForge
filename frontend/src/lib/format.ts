import { format, formatDistanceToNow } from "date-fns";

export const formatNumber = (n: number | string, digits = 4): string => {
  const v = typeof n === "string" ? parseFloat(n) : n;
  if (Number.isNaN(v)) return "—";
  if (Math.abs(v) >= 1e9) return `${(v / 1e9).toFixed(2)}B`;
  if (Math.abs(v) >= 1e6) return `${(v / 1e6).toFixed(2)}M`;
  if (Math.abs(v) >= 1e3) return `${(v / 1e3).toFixed(2)}K`;
  return v.toFixed(digits);
};

export const formatPercent = (n: number | string, digits = 2): string => {
  const v = typeof n === "string" ? parseFloat(n) : n;
  if (Number.isNaN(v)) return "—";
  return `${(v * 100).toFixed(digits)}%`;
};

export const formatDate = (input: string | Date): string =>
  format(typeof input === "string" ? new Date(input) : input, "yyyy-MM-dd HH:mm");

export const formatRelative = (input: string | Date): string =>
  formatDistanceToNow(typeof input === "string" ? new Date(input) : input, { addSuffix: true });

export const truncateAddr = (addr: string, head = 6, tail = 4): string =>
  addr.length > head + tail ? `${addr.slice(0, head)}…${addr.slice(-tail)}` : addr;

export const severityClass = (severity: string): string => {
  switch (severity) {
    case "critical": return "bg-rose-700/30 text-rose-200 border-rose-700/40";
    case "high":     return "bg-orange-600/20 text-orange-200 border-orange-700/40";
    case "medium":   return "bg-yellow-500/20 text-yellow-200 border-yellow-600/40";
    case "low":      return "bg-emerald-600/20 text-emerald-200 border-emerald-700/40";
    default:         return "bg-slate-600/20 text-slate-200 border-slate-700/40";
  }
};
