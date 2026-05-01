import { Card } from "@/components/ui/Card";

type Item = { kind: string; label: string; params: Record<string, unknown>; group: string };

const items: Item[] = [
  { group: "Indicators", kind: "indicator", label: "EMA", params: { name: "ema", alias: "fast", period: 12 } },
  { group: "Indicators", kind: "indicator", label: "EMA slow", params: { name: "ema", alias: "slow", period: 26 } },
  { group: "Indicators", kind: "indicator", label: "RSI", params: { name: "rsi", alias: "rsi14", period: 14 } },
  { group: "Indicators", kind: "indicator", label: "MACD", params: { name: "macd", alias: "macd", fast: 12, slow: 26, signal: 9 } },
  { group: "Indicators", kind: "indicator", label: "Bollinger", params: { name: "bollinger", alias: "bb", period: 20, k: 2.0 } },
  { group: "Indicators", kind: "indicator", label: "ATR", params: { name: "atr", alias: "atr14", period: 14 } },
  { group: "Indicators", kind: "indicator", label: "VWAP", params: { name: "vwap", alias: "vwap" } },
  { group: "Indicators", kind: "indicator", label: "Supertrend", params: { name: "supertrend", alias: "st", atr_period: 10, multiplier: 3.0 } },
  { group: "Operators", kind: "operator", label: "cross_up()", params: { fn: "cross_up" } },
  { group: "Operators", kind: "operator", label: "cross_down()", params: { fn: "cross_down" } },
  { group: "Operators", kind: "operator", label: ">", params: { fn: ">" } },
  { group: "Operators", kind: "operator", label: "<", params: { fn: "<" } },
  { group: "Operators", kind: "operator", label: "and", params: { fn: "and" } },
  { group: "Operators", kind: "operator", label: "or", params: { fn: "or" } },
  { group: "Constants", kind: "constant", label: "Number", params: { value: 0 } },
  { group: "Constants", kind: "constant", label: "Symbol ref", params: { value: "fast" } },
  { group: "Rules", kind: "rule", label: "Buy rule", params: { action: "buy", size: 0.2 } },
  { group: "Rules", kind: "rule", label: "Sell rule", params: { action: "sell", size: 1.0 } },
  { group: "Rules", kind: "rule", label: "Close rule", params: { action: "close" } },
  { group: "Rules", kind: "rule", label: "Alert rule", params: { action: "alert" } },
  { group: "Triggers", kind: "trigger", label: "On candle close", params: { event: "candle_close" } },
];

const groups = Array.from(new Set(items.map((i) => i.group)));

type Props = {
  onAdd: (kind: string, label: string, params: Record<string, unknown>) => void;
};

export const Palette = ({ onAdd }: Props) => (
  <div className="space-y-3">
    {groups.map((g) => (
      <div key={g}>
        <div className="text-[11px] uppercase text-slate-500 mb-1 tracking-wide">{g}</div>
        <div className="grid grid-cols-1 gap-1">
          {items.filter((i) => i.group === g).map((i) => (
            <button
              key={i.label}
              onClick={() => onAdd(i.kind, i.label, i.params)}
              className="text-left text-sm bg-slate-900/40 border border-white/5 rounded-md px-2 py-1.5 hover:bg-white/10"
            >
              {i.label}
            </button>
          ))}
        </div>
      </div>
    ))}
  </div>
);
