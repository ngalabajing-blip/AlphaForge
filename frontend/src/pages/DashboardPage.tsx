import { useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis,
} from "recharts";

import api from "@/lib/api";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { formatNumber, formatRelative, severityClass } from "@/lib/format";

type Ticker = { symbol: string; price: string; ts: string };
type DominanceResp = { quote: string; values: Record<string, number> };
type Mover = { symbol: string; price: string; change_pct: number };

export default function DashboardPage() {
  const tickers = useQuery({
    queryKey: ["dashboard.tickers"],
    queryFn: async () => {
      const symbols = ["BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT", "ARB/USDT"];
      const results = await Promise.all(symbols.map(async (s) => {
        try {
          const r = await api.get<Ticker>(`/market/ticker/${encodeURIComponent(s)}`);
          return r.data;
        } catch {
          return { symbol: s, price: "0", ts: new Date().toISOString() };
        }
      }));
      return results;
    },
    refetchInterval: 30000,
  });

  const candles = useQuery({
    queryKey: ["dashboard.candles"],
    queryFn: async () => {
      try {
        const r = await api.get<{ candles: { ts: string; close: string }[] }>(
          "/market/candles/ETH/USDT",
          { params: { timeframe: "1h", limit: 96 } },
        );
        return (r.data?.candles || []).map((c) => ({ ts: String(c.ts || "").slice(5, 16), close: parseFloat(c.close) || 0 }));
      } catch {
        return [] as { ts: string; close: number }[];
      }
    },
    refetchInterval: 60000,
  });

  const dominance = useQuery({
    queryKey: ["dashboard.dominance"],
    queryFn: async () => {
      try {
        const r = await api.get<DominanceResp>("/market/dominance");
        return r.data;
      } catch {
        return null;
      }
    },
    refetchInterval: 60000,
  });

  const movers = useQuery({
    queryKey: ["dashboard.movers"],
    queryFn: async () => {
      try {
        const r = await api.get<{ direction: string; movers: Mover[] }>("/market/movers", { params: { direction: "up", n: 8 } });
        return r.data?.movers || [];
      } catch {
        return [] as Mover[];
      }
    },
    refetchInterval: 60000,
  });

  const audits = useQuery({
    queryKey: ["dashboard.audits"],
    queryFn: async () => {
      try {
        const r = await api.get<{ items: { id: string; chain: string; address: string; risk_level: string; status: string; created_at: string }[] }>("/audits", { params: { limit: 5 } });
        return r.data?.items || [];
      } catch {
        return [] as { id: string; chain: string; address: string; risk_level: string; status: string; created_at: string }[];
      }
    },
    refetchInterval: 60000,
  });

  const total = useMemo(() => tickers.data?.length ?? 0, [tickers.data]);

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
      <Card title="Live Tickers" subtitle={`${total} symbols streaming`} className="lg:col-span-2">
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
          {tickers.data?.map((t) => (
            <div key={t.symbol} className="bg-slate-900/40 rounded-lg p-3 border border-white/5">
              <div className="text-xs text-slate-400">{t.symbol}</div>
              <div className="text-lg font-mono">{formatNumber(t.price ?? "0", 2)}</div>
              <div className="text-[10px] text-slate-500">{t.ts ? formatRelative(t.ts) : "—"}</div>
            </div>
          ))}
          {tickers.isLoading && <div className="text-slate-500 text-sm col-span-full">Loading market data...</div>}
          {!tickers.isLoading && (!tickers.data || tickers.data.length === 0) && <div className="text-slate-500 text-sm col-span-full">No ticker data available</div>}
        </div>
      </Card>

      <Card title="Dominance" subtitle="Market share">
        <ul className="space-y-2 text-sm">
          {dominance.data?.values ? (
            Object.entries(dominance.data.values)
              .sort((a, b) => b[1] - a[1])
              .map(([k, v]) => (
                <li key={k} className="flex items-center justify-between">
                  <span>{k}</span>
                  <Badge tone="primary">{typeof v === "number" ? v.toFixed(1) : "0.0"}%</Badge>
                </li>
              ))
          ) : (
            <li className="text-slate-500 text-sm">{dominance.isLoading ? "Loading..." : "No data"}</li>
          )}
        </ul>
      </Card>

      <Card title="ETH/USDT — 96 hour close" className="lg:col-span-2">
        <div style={{ width: "100%", height: 220 }}>
          {candles.data && candles.data.length > 0 ? (
            <ResponsiveContainer>
              <AreaChart data={candles.data}>
                <defs>
                  <linearGradient id="ethGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#22d3ee" stopOpacity={0.5} />
                    <stop offset="95%" stopColor="#22d3ee" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="ts" stroke="#64748b" fontSize={10} />
                <YAxis stroke="#64748b" fontSize={10} domain={["auto", "auto"]} />
                <Tooltip contentStyle={{ background: "#0f172a", border: "1px solid #1e293b" }} labelStyle={{ color: "#cbd5e1" }} />
                <Area type="monotone" dataKey="close" stroke="#22d3ee" fill="url(#ethGrad)" />
              </AreaChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex items-center justify-center h-full text-slate-500 text-sm">
              {candles.isLoading ? "Loading chart..." : "No chart data available"}
            </div>
          )}
        </div>
      </Card>

      <Card title="Top Movers (24h)">
        <ul className="space-y-2">
          {movers.data && movers.data.length > 0 ? (
            movers.data.map((m) => (
              <li key={m.symbol} className="flex items-center justify-between text-sm">
                <span>{m.symbol}</span>
                <Badge tone={(m.change_pct ?? 0) > 0 ? "bullish" : "bearish"}>
                  {((m.change_pct ?? 0) * 100).toFixed(2)}%
                </Badge>
              </li>
            ))
          ) : (
            <li className="text-slate-500 text-sm">{movers.isLoading ? "Loading..." : "No movers data"}</li>
          )}
        </ul>
      </Card>

      <Card title="Recent Audits" className="lg:col-span-3">
        <div className="overflow-x-auto">
          {audits.data && audits.data.length > 0 ? (
            <table className="min-w-full text-sm">
              <thead className="text-xs text-slate-400 uppercase">
                <tr>
                  <th className="text-left py-2">Chain</th>
                  <th className="text-left py-2">Address</th>
                  <th className="text-left py-2">Status</th>
                  <th className="text-left py-2">Severity</th>
                  <th className="text-left py-2">Created</th>
                </tr>
              </thead>
              <tbody>
                {audits.data.map((a) => (
                  <tr key={a.id} className="border-t border-white/5">
                    <td className="py-2">{a.chain}</td>
                    <td className="py-2 font-mono text-xs">{a.address}</td>
                    <td className="py-2"><Badge tone="neutral">{a.status}</Badge></td>
                    <td className="py-2">
                      <span className={`px-2 py-0.5 text-xs rounded border ${severityClass(a.risk_level)}`}>{a.risk_level}</span>
                    </td>
                    <td className="py-2 text-slate-400 text-xs">{a.created_at ? formatRelative(a.created_at) : "—"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <div className="text-slate-500 text-sm py-4">{audits.isLoading ? "Loading audits..." : "No recent audits"}</div>
          )}
        </div>
      </Card>
    </div>
  );
}
