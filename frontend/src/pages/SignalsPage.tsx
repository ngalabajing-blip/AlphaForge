import { useState } from "react";

import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { useApiQuery } from "@/hooks/useApi";
import { useWebSocket } from "@/hooks/useWebSocket";
import { formatRelative } from "@/lib/format";

type Signal = {
  id: string;
  strategy_id: string;
  symbol: string;
  action: string;
  strength: number;
  emitted_at: string;
  reasons: string[];
};

export default function SignalsPage() {
  const { data } = useApiQuery<{ items: Signal[] }>(["signals.list"], "/signals?limit=200");
  const [live, setLive] = useState<unknown[]>([]);
  useWebSocket("/ws/signals", {
    onMessage: (m) => setLive((prev) => [m, ...prev].slice(0, 50)),
  });

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
      <Card title="Recent signals" className="lg:col-span-2">
        <div className="overflow-x-auto">
          <table className="min-w-full text-sm">
            <thead className="text-xs text-slate-400 uppercase">
              <tr>
                <th className="text-left py-2">Symbol</th>
                <th className="text-left py-2">Action</th>
                <th className="text-right py-2">Strength</th>
                <th className="text-left py-2">Reasons</th>
                <th className="text-left py-2">Emitted</th>
              </tr>
            </thead>
            <tbody>
              {data?.items?.map((s) => (
                <tr key={s.id} className="border-t border-white/5">
                  <td className="py-2 font-mono text-xs">{s.symbol}</td>
                  <td className="py-2">
                    <Badge tone={s.action === "buy" ? "bullish" : s.action === "sell" ? "bearish" : "neutral"}>
                      {s.action}
                    </Badge>
                  </td>
                  <td className="py-2 text-right">{s.strength.toFixed(2)}</td>
                  <td className="py-2 text-xs text-slate-400">
                    {(s.reasons || []).slice(0, 4).map((r, i) => (
                      <span key={i} className="inline-block mr-2">{r}</span>
                    ))}
                  </td>
                  <td className="py-2 text-xs text-slate-400">{formatRelative(s.emitted_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>

      <Card title="Live feed" subtitle="WebSocket /ws/signals">
        <ul className="space-y-2 max-h-[480px] overflow-auto text-xs font-mono">
          {live.length === 0 && <li className="text-slate-500">awaiting heartbeat…</li>}
          {live.map((m, i) => (
            <li key={i} className="border-l-2 border-primary-500 pl-2">
              <pre className="whitespace-pre-wrap">{JSON.stringify(m, null, 2)}</pre>
            </li>
          ))}
        </ul>
      </Card>
    </div>
  );
}
