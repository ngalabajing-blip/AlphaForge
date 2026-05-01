import clsx from "clsx";
import { PropsWithChildren } from "react";

type Props = PropsWithChildren<{
  tone?: "neutral" | "primary" | "bullish" | "bearish" | "warning" | "info";
  className?: string;
}>;

export const Badge = ({ tone = "neutral", className, children }: Props) => {
  const styles: Record<string, string> = {
    neutral: "bg-slate-700/40 text-slate-200",
    primary: "bg-primary-600/20 text-primary-100 border border-primary-700/40",
    bullish: "bg-emerald-700/30 text-emerald-200 border border-emerald-700/40",
    bearish: "bg-rose-700/30 text-rose-200 border border-rose-700/40",
    warning: "bg-amber-600/30 text-amber-200 border border-amber-700/40",
    info: "bg-cyan-700/30 text-cyan-200 border border-cyan-700/40",
  };
  return (
    <span
      className={clsx(
        "inline-flex items-center gap-1 rounded-md text-xs font-medium px-2 py-0.5",
        styles[tone],
        className,
      )}
    >
      {children}
    </span>
  );
};
