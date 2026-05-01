import { Link } from "react-router-dom";

import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { useApiQuery } from "@/hooks/useApi";
import { formatRelative } from "@/lib/format";

type BacktestSummary = {
  id: string;
  strategy_id: string;
  strategy_version: number;
  status: string;
  pnl_pct?: string;
  sharpe?: string;
  max_drawdown?: string;
  trades_count?: number;
  created_at: string;
};

export default function BacktestsPage() {
  const { data, isLoading } = useApiQuery<{ items: BacktestSummary[] }>(
    ["backtests.list"],
    "/backtests?limit=200",
  );
  const items = data?.items || [];
  if (isLoading) return <div className="text-sm text-slate-400">Loading backtests…</div>;

  return (
    <Card title="Backtests" subtitle={`${items.length} run(s)`}>
      <div className="overflow-x-auto">
        <table className="min-w-full text-sm">
          <thead className="text-xs text-slate-400 uppercase">
            <tr>
              <th className="text-left py-2">ID</th>
              <th className="text-left py-2">Strategy</th>
              <th className="text-left py-2">Version</th>
              <th className="text-left py-2">Status</th>
              <th className="text-right py-2">PnL %</th>
              <th className="text-right py-2">Sharpe</th>
              <th className="text-right py-2">Max DD</th>
              <th className="text-right py-2">Trades</th>
              <th className="text-left py-2">Created</th>
            </tr>
          </thead>
          <tbody>
            {items.map((b) => (
              <tr key={b.id} className="border-t border-white/5 hover:bg-white/5">
                <td className="py-2"><Link to={`/backtests/${b.id}`} className="text-primary-300">{b.id.slice(0, 8)}</Link></td>
                <td className="py-2 font-mono text-xs">{b.strategy_id.slice(0, 8)}</td>
                <td className="py-2">{b.strategy_version}</td>
                <td className="py-2">
                  <Badge tone={b.status === "completed" ? "bullish" : b.status === "failed" ? "bearish" : "neutral"}>
                    {b.status}
                  </Badge>
                </td>
                <td className="py-2 text-right">{b.pnl_pct ?? "—"}</td>
                <td className="py-2 text-right">{b.sharpe ?? "—"}</td>
                <td className="py-2 text-right">{b.max_drawdown ?? "—"}</td>
                <td className="py-2 text-right">{b.trades_count ?? "—"}</td>
                <td className="py-2 text-xs text-slate-400">{formatRelative(b.created_at)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Card>
  );
}
