import { Link } from "react-router-dom";

import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { EmptyState } from "@/components/ui/EmptyState";
import { useApiQuery } from "@/hooks/useApi";
import { formatRelative } from "@/lib/format";

type StrategyOut = {
  id: string;
  name: string;
  description?: string;
  is_public: boolean;
  is_archived: boolean;
  tags: string[];
  latest_version: number;
  created_at: string;
};

export default function StrategiesPage() {
  const { data, isLoading } = useApiQuery<{ items: StrategyOut[]; total: number }>(
    ["strategies.list"],
    "/strategies?limit=200",
  );

  if (isLoading) return <div className="text-slate-400 text-sm">Loading strategies…</div>;
  const items = data?.items?.filter((s) => !s.is_archived) || [];

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold">Strategies</h2>
          <p className="text-xs text-slate-400">
            Versioned, declarative trading playbooks compiled from the Strategy DSL.
          </p>
        </div>
        <Link to="/strategies/builder" className="btn-primary">
          + New strategy
        </Link>
      </div>

      {items.length === 0 ? (
        <Card>
          <EmptyState
            icon="🧠"
            title="No strategies yet"
            description="Open the visual builder to compose your first DSL strategy."
            action={<Link to="/strategies/builder" className="btn-primary">Open builder</Link>}
          />
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {items.map((s) => (
            <Card key={s.id} title={s.name} subtitle={formatRelative(s.created_at)}
              action={<Badge tone={s.is_public ? "info" : "neutral"}>{s.is_public ? "public" : "private"}</Badge>}>
              <p className="text-sm text-slate-300 mb-3 line-clamp-2">{s.description || "No description."}</p>
              <div className="flex flex-wrap gap-1 mb-3">
                {s.tags?.map((t) => <Badge key={t} tone="primary">{t}</Badge>)}
              </div>
              <div className="flex items-center justify-between text-xs text-slate-400">
                <span>v{s.latest_version}</span>
                <Link to={`/strategies/builder/${s.id}`} className="text-primary-300 hover:underline">
                  open builder →
                </Link>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
