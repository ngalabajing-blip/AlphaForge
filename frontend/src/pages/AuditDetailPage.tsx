import { useParams } from "react-router-dom";

import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { useApiQuery } from "@/hooks/useApi";
import { formatRelative, severityClass, truncateAddr } from "@/lib/format";

type Finding = {
  category: string;
  code: string;
  severity: string;
  description: string;
  occurrences?: number;
};

type Audit = {
  id: string;
  chain: string;
  address: string;
  status: string;
  risk_score?: number;
  risk_level?: string;
  summary?: string;
  findings: Finding[];
  bytecode_size?: number;
  has_source?: boolean;
  started_at?: string | null;
  completed_at?: string | null;
  created_at: string;
};

export default function AuditDetailPage() {
  const { id } = useParams<{ id: string }>();
  const { data, isLoading } = useApiQuery<Audit>(["audits.detail", id], `/audits/${id}`);
  if (isLoading || !data) return <div className="text-sm text-slate-400">Loading…</div>;

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold">Audit {data.id.slice(0, 8)}</h2>
          <p className="text-xs text-slate-400">
            {data.chain} · {truncateAddr(data.address, 8, 6)} · {formatRelative(data.created_at)}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Badge tone="neutral">{data.status}</Badge>
          {data.risk_level && (
            <span className={`px-2 py-0.5 text-xs rounded border ${severityClass(data.risk_level)}`}>
              {data.risk_level}
            </span>
          )}
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <Stat label="Risk score" value={String(data.risk_score ?? "—")} />
        <Stat label="Findings" value={String(data.findings?.length ?? 0)} />
        <Stat label="Bytecode" value={data.bytecode_size ? `${data.bytecode_size}B` : "—"} />
        <Stat label="Source" value={data.has_source ? "verified" : "unverified"} />
      </div>

      <Card title="Summary">
        <p className="text-sm text-slate-300">{data.summary || "No summary."}</p>
      </Card>

      <Card title="Findings" subtitle={`${data.findings?.length ?? 0} items`}>
        {data.findings?.length ? (
          <div className="space-y-2">
            {data.findings.map((f, idx) => (
              <div
                key={idx}
                className={`rounded-lg p-3 border ${severityClass(f.severity)}`}
              >
                <div className="flex items-center justify-between text-xs">
                  <span className="font-mono">{f.code}</span>
                  <span className="uppercase">{f.severity}</span>
                </div>
                <div className="text-sm mt-1">{f.description}</div>
                <div className="text-[11px] text-slate-400 mt-1">
                  category: {f.category}
                  {f.occurrences != null && ` · occurrences: ${f.occurrences}`}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-sm text-slate-400">No findings reported.</p>
        )}
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
