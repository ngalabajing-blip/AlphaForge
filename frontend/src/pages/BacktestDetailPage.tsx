import { useParams } from "react-router-dom";
import {
  Bar, BarChart, CartesianGrid, Cell, Line, LineChart, ResponsiveContainer,
  Tooltip, XAxis, YAxis,
} from "recharts";

import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { useApiQuery } from "@/hooks/useApi";
import { formatRelative, formatNumber } from "@/lib/format";

type Trade = {
  opened_at: string;
  closed_at?: string | null;
  symbol: string;
  side: string;
  entry_price: string;
  exit_price?: string | null;
  quantity: string;
  pnl?: string;
};

type Backtest = {
  id: string;
  status: string;
  strategy_id: string;
  strategy_version: number;
  start_at: string;
  end_at: string;
  initial_balance: string;
  final_balance?: string;
  pnl_abs?: string;
  pnl_pct?: string;
  sharpe?: string;
  sortino?: string;
  max_drawdown?: string;
  win_rate?: string;
  trades_count?: number;
  metrics?: Record<string, number>;
  trades: Trade[];
  created_at: string;
};

export default function BacktestDetailPage() {
  const { id } = useParams<{ id: string }>();
  const { data, isLoading } = useApiQuery<Backtest>(["backtests.detail", id], `/backtests/${id}`);
  if (isLoading || !data) return <div className="text-sm text-slate-400">Loading…</div>;

  const trades = data.trades || [];
  const equityCurve = trades.reduce<{ ts: string; pnl: number }[]>((acc, t, i) => {
    const last = acc[i - 1]?.pnl ?? 0;
    return [...acc, { ts: t.closed_at || t.opened_at, pnl: last + parseFloat(t.pnl || "0") }];
  }, []);

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold">Backtest {data.id.slice(0, 8)}</h2>
          <p className="text-xs text-slate-400">{formatRelative(data.created_at)}</p>
        </div>
        <Badge tone={data.status === "completed" ? "bullish" : data.status === "failed" ? "bearish" : "neutral"}>
          {data.status}
        </Badge>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <Stat label="Initial" value={formatNumber(data.initial_balance, 2)} />
        <Stat label="Final" value={data.final_balance ? formatNumber(data.final_balance, 2) : "—"} />
        <Stat label="PnL %" value={data.pnl_pct ? `${data.pnl_pct}%` : "—"} />
        <Stat label="Sharpe" value={data.sharpe ?? "—"} />
        <Stat label="Sortino" value={data.sortino ?? "—"} />
        <Stat label="Max DD" value={data.max_drawdown ? `${data.max_drawdown}` : "—"} />
        <Stat label="Win rate" value={data.win_rate ? `${data.win_rate}%` : "—"} />
        <Stat label="Trades" value={String(data.trades_count ?? 0)} />
      </div>

      <Card title="Cumulative PnL">
        <div style={{ width: "100%", height: 240 }}>
          <ResponsiveContainer>
            <LineChart data={equityCurve}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis dataKey="ts" stroke="#64748b" fontSize={10} hide />
              <YAxis stroke="#64748b" fontSize={10} />
              <Tooltip contentStyle={{ background: "#0f172a", border: "1px solid #1e293b" }} />
              <Line type="monotone" dataKey="pnl" stroke="#22d3ee" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </Card>

      <Card title="Trade-level PnL">
        <div style={{ width: "100%", height: 220 }}>
          <ResponsiveContainer>
            <BarChart data={trades.map((t) => ({ symbol: t.symbol, pnl: parseFloat(t.pnl || "0") }))}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis dataKey="symbol" stroke="#64748b" fontSize={10} hide />
              <YAxis stroke="#64748b" fontSize={10} />
              <Tooltip contentStyle={{ background: "#0f172a", border: "1px solid #1e293b" }} />
              <Bar dataKey="pnl">
                {trades.map((t, idx) => (
                  <Cell key={idx} fill={parseFloat(t.pnl || "0") >= 0 ? "#16a34a" : "#dc2626"} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </Card>

      <Card title="Trade list" subtitle={`${trades.length} fills`}>
        <div className="overflow-x-auto">
          <table className="min-w-full text-sm">
            <thead className="text-xs text-slate-400 uppercase">
              <tr>
                <th className="text-left py-2">Symbol</th>
                <th className="text-left py-2">Side</th>
                <th className="text-right py-2">Entry</th>
                <th className="text-right py-2">Exit</th>
                <th className="text-right py-2">Qty</th>
                <th className="text-right py-2">PnL</th>
                <th className="text-left py-2">Opened</th>
              </tr>
            </thead>
            <tbody>
              {trades.map((t, i) => (
                <tr key={i} className="border-t border-white/5">
                  <td className="py-2">{t.symbol}</td>
                  <td className="py-2">
                    <Badge tone={t.side === "buy" ? "bullish" : "bearish"}>{t.side}</Badge>
                  </td>
                  <td className="py-2 text-right">{formatNumber(t.entry_price, 4)}</td>
                  <td className="py-2 text-right">{t.exit_price ? formatNumber(t.exit_price, 4) : "—"}</td>
                  <td className="py-2 text-right">{formatNumber(t.quantity, 4)}</td>
                  <td className="py-2 text-right">
                    <span className={parseFloat(t.pnl || "0") >= 0 ? "text-emerald-400" : "text-rose-400"}>
                      {t.pnl ? formatNumber(t.pnl, 2) : "—"}
                    </span>
                  </td>
                  <td className="py-2 text-xs text-slate-400">{formatRelative(t.opened_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}

const Stat = ({ label, value }: { label: string; value: string }) => (
  <div className="bg-slate-900/40 rounded-lg p-3 border border-white/5">
    <div className="text-[10px] text-slate-400 uppercase">{label}</div>
    <div className="text-base font-mono">{value}</div>
  </div>
);
