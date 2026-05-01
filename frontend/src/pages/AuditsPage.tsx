import { useState } from "react";
import { Link } from "react-router-dom";

import api from "@/lib/api";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { useApiQuery } from "@/hooks/useApi";
import { formatRelative, severityClass, truncateAddr } from "@/lib/format";

type AuditOut = {
  id: string;
  chain: string;
  address: string;
  status: string;
  risk_score?: number;
  risk_level?: string;
  summary?: string;
  created_at: string;
};

export default function AuditsPage() {
  const { data, refetch } = useApiQuery<{ items: AuditOut[] }>(["audits.list"], "/audits?limit=200");
  const [chain, setChain] = useState("eth");
  const [address, setAddress] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await api.post("/audits", { chain, address, deep: true });
      setAddress("");
      await refetch();
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="space-y-5">
      <Card title="Request a smart contract audit">
        <form onSubmit={submit} className="flex flex-wrap gap-2 items-end">
          <label className="space-y-1">
            <span className="text-xs text-slate-400">Chain</span>
            <select
              value={chain}
              onChange={(e) => setChain(e.target.value)}
              className="bg-slate-900/40 border border-white/10 rounded-md px-2 py-1 text-sm"
            >
              {["eth", "bsc", "polygon", "arbitrum", "base", "optimism", "avalanche"].map((c) => (
                <option key={c} value={c}>{c}</option>
              ))}
            </select>
          </label>
          <label className="flex-1 min-w-[260px] space-y-1">
            <span className="text-xs text-slate-400">Address</span>
            <input
              required
              value={address}
              onChange={(e) => setAddress(e.target.value)}
              placeholder="0x…"
              className="w-full bg-slate-900/40 border border-white/10 rounded-md px-2 py-1.5 text-sm font-mono"
            />
          </label>
          <button type="submit" className="btn-primary" disabled={submitting}>
            {submitting ? "Queueing…" : "Audit contract"}
          </button>
        </form>
      </Card>

      <Card title="Recent audits" subtitle={`${data?.items?.length || 0} jobs`}>
        <div className="overflow-x-auto">
          <table className="min-w-full text-sm">
            <thead className="text-xs text-slate-400 uppercase">
              <tr>
                <th className="text-left py-2">Chain</th>
                <th className="text-left py-2">Address</th>
                <th className="text-left py-2">Status</th>
                <th className="text-right py-2">Score</th>
                <th className="text-left py-2">Severity</th>
                <th className="text-left py-2">Summary</th>
                <th className="text-left py-2">Created</th>
              </tr>
            </thead>
            <tbody>
              {data?.items?.map((a) => (
                <tr key={a.id} className="border-t border-white/5 hover:bg-white/5">
                  <td className="py-2">{a.chain}</td>
                  <td className="py-2 font-mono text-xs">
                    <Link to={`/audits/${a.id}`} className="text-primary-300">
                      {truncateAddr(a.address)}
                    </Link>
                  </td>
                  <td className="py-2"><Badge tone="neutral">{a.status}</Badge></td>
                  <td className="py-2 text-right">{a.risk_score ?? "—"}</td>
                  <td className="py-2">
                    {a.risk_level && (
                      <span className={`px-2 py-0.5 text-xs rounded border ${severityClass(a.risk_level)}`}>
                        {a.risk_level}
                      </span>
                    )}
                  </td>
                  <td className="py-2 text-xs text-slate-300 max-w-[300px] truncate">{a.summary || "—"}</td>
                  <td className="py-2 text-xs text-slate-400">{formatRelative(a.created_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}
