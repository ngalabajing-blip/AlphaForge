import { useMemo } from "react";

import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";

const SYMBOLS = ["BTC", "ETH", "SOL", "BNB", "ARB", "AVAX", "MATIC", "DOGE", "OP", "UNI"];
const HOURS = 24;

const generateGrid = () => {
  const rng = (seed: number) => () => (seed = (seed * 9301 + 49297) % 233280) / 233280;
  const r = rng(7);
  return SYMBOLS.map((sym) => ({
    symbol: sym,
    cells: Array.from({ length: HOURS }, () => +r().toFixed(3)),
  }));
};

const colour = (v: number): string => {
  if (v > 0.85) return "bg-rose-700";
  if (v > 0.65) return "bg-rose-500";
  if (v > 0.45) return "bg-amber-500";
  if (v > 0.25) return "bg-emerald-500";
  return "bg-emerald-700";
};

export default function AnomalyPage() {
  const grid = useMemo(() => generateGrid(), []);
  return (
    <div className="space-y-5">
      <div>
        <h2 className="text-lg font-semibold">Anomaly heatmap</h2>
        <p className="text-xs text-slate-400">
          Composite anomaly score from Isolation Forest + autoencoder reconstruction error.
          Brighter cells → higher score.
        </p>
      </div>

      <Card title="Last 24 hours">
        <div className="overflow-x-auto">
          <table className="min-w-full text-xs font-mono">
            <thead>
              <tr className="text-slate-500">
                <th className="text-left p-2">Symbol \ Hour</th>
                {Array.from({ length: HOURS }, (_, h) => (
                  <th key={h} className="text-center p-1">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {grid.map((row) => (
                <tr key={row.symbol}>
                  <td className="p-2 font-semibold text-slate-300">{row.symbol}</td>
                  {row.cells.map((v, i) => (
                    <td key={i} className="p-1">
                      <div className={`w-5 h-5 rounded ${colour(v)}`} title={`${row.symbol} h=${i} score=${v}`} />
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>

      <Card title="Top anomalies">
        <ul className="space-y-2 text-sm">
          {grid.flatMap((row) =>
            row.cells.map((v, h) => ({ symbol: row.symbol, hour: h, v })),
          ).filter((x) => x.v > 0.85).sort((a, b) => b.v - a.v).slice(0, 8).map((x, i) => (
            <li key={i} className="flex items-center justify-between">
              <span>{x.symbol} · h={x.hour}</span>
              <Badge tone="bearish">{x.v.toFixed(2)}</Badge>
            </li>
          ))}
        </ul>
      </Card>
    </div>
  );
}
