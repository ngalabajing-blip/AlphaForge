import { useState } from "react";

import api from "@/lib/api";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { useApiQuery } from "@/hooks/useApi";
import { formatRelative } from "@/lib/format";

type APIKeyOut = {
  id: string;
  label: string;
  scopes: string[];
  created_at: string;
  last_used_at?: string | null;
  expires_at?: string | null;
  revoked_at?: string | null;
};

type APIKeyCreated = APIKeyOut & { token: string };

export default function SettingsPage() {
  const [label, setLabel] = useState("My key");
  const [created, setCreated] = useState<APIKeyCreated | null>(null);
  const { data, refetch } = useApiQuery<APIKeyOut[]>(["api-keys"], "/api-keys");

  const create = async () => {
    const r = await api.post<APIKeyCreated>("/api-keys", { label, scopes: ["read"] });
    setCreated(r.data);
    refetch();
  };
  const revoke = async (id: string) => {
    await api.delete(`/api-keys/${id}`);
    refetch();
  };

  return (
    <div className="space-y-5">
      <Card title="API keys" subtitle="Use X-API-Key header for service-to-service access">
        <div className="flex items-end gap-2 mb-4">
          <label className="flex-1">
            <span className="text-xs text-slate-400 block mb-1">Label</span>
            <input
              value={label}
              onChange={(e) => setLabel(e.target.value)}
              className="w-full bg-slate-900/40 border border-white/10 rounded-md px-2 py-1.5 text-sm"
            />
          </label>
          <button className="btn-primary" onClick={create}>Generate</button>
        </div>
        {created && (
          <div className="mb-4 p-3 rounded-lg border border-emerald-700/40 bg-emerald-900/20 text-sm font-mono break-all">
            <div className="text-emerald-300 text-xs uppercase">Copy now — shown only once</div>
            {created.token}
          </div>
        )}
        <div className="overflow-x-auto">
          <table className="min-w-full text-sm">
            <thead className="text-xs text-slate-400 uppercase">
              <tr>
                <th className="text-left py-2">Label</th>
                <th className="text-left py-2">Scopes</th>
                <th className="text-left py-2">Last used</th>
                <th className="text-left py-2">Created</th>
                <th className="text-left py-2">Actions</th>
              </tr>
            </thead>
            <tbody>
              {(data || []).map((k) => (
                <tr key={k.id} className="border-t border-white/5">
                  <td className="py-2">{k.label}</td>
                  <td className="py-2 space-x-1">
                    {k.scopes.map((s) => <Badge key={s} tone="primary">{s}</Badge>)}
                  </td>
                  <td className="py-2 text-xs text-slate-400">
                    {k.last_used_at ? formatRelative(k.last_used_at) : "never"}
                  </td>
                  <td className="py-2 text-xs text-slate-400">{formatRelative(k.created_at)}</td>
                  <td className="py-2">
                    <button className="btn-danger" onClick={() => revoke(k.id)} disabled={!!k.revoked_at}>
                      {k.revoked_at ? "revoked" : "revoke"}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}
