import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { useApiQuery } from "@/hooks/useApi";
import { formatRelative } from "@/lib/format";

type Alert = {
  id: string;
  name: string;
  rule_type: string;
  enabled: boolean;
  fire_count: number;
  last_fired_at?: string | null;
  channels: string[];
  created_at: string;
};

export default function AlertsPage() {
  const { data } = useApiQuery<{ items: Alert[] }>(["alerts.list"], "/alerts?limit=200");
  const items = data?.items || [];
  return (
    <Card title="Alerts" subtitle={`${items.length} configured`}>
      <div className="overflow-x-auto">
        <table className="min-w-full text-sm">
          <thead className="text-xs text-slate-400 uppercase">
            <tr>
              <th className="text-left py-2">Name</th>
              <th className="text-left py-2">Rule</th>
              <th className="text-left py-2">Channels</th>
              <th className="text-right py-2">Fired</th>
              <th className="text-left py-2">Last fired</th>
              <th className="text-left py-2">State</th>
            </tr>
          </thead>
          <tbody>
            {items.map((a) => (
              <tr key={a.id} className="border-t border-white/5">
                <td className="py-2">{a.name}</td>
                <td className="py-2">{a.rule_type}</td>
                <td className="py-2 space-x-1">
                  {(a.channels || []).map((c) => (
                    <Badge key={c} tone="info">{c}</Badge>
                  ))}
                </td>
                <td className="py-2 text-right">{a.fire_count}</td>
                <td className="py-2 text-xs text-slate-400">
                  {a.last_fired_at ? formatRelative(a.last_fired_at) : "—"}
                </td>
                <td className="py-2">
                  <Badge tone={a.enabled ? "bullish" : "neutral"}>
                    {a.enabled ? "active" : "paused"}
                  </Badge>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Card>
  );
}
