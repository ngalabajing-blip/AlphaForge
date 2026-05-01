import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { useApiQuery } from "@/hooks/useApi";
import { formatRelative } from "@/lib/format";

type UserOut = {
  id: string;
  email: string;
  full_name?: string | null;
  role: string;
  is_active: boolean;
  last_login_at?: string | null;
  created_at: string;
};

export default function AdminPage() {
  const { data } = useApiQuery<{ items: UserOut[]; total: number }>(["admin.users"], "/users?limit=200");
  return (
    <Card title="Users" subtitle={`${data?.total ?? 0} accounts`}>
      <div className="overflow-x-auto">
        <table className="min-w-full text-sm">
          <thead className="text-xs text-slate-400 uppercase">
            <tr>
              <th className="text-left py-2">Email</th>
              <th className="text-left py-2">Name</th>
              <th className="text-left py-2">Role</th>
              <th className="text-left py-2">Active</th>
              <th className="text-left py-2">Last login</th>
              <th className="text-left py-2">Created</th>
            </tr>
          </thead>
          <tbody>
            {data?.items?.map((u) => (
              <tr key={u.id} className="border-t border-white/5">
                <td className="py-2">{u.email}</td>
                <td className="py-2">{u.full_name || "—"}</td>
                <td className="py-2"><Badge tone="primary">{u.role}</Badge></td>
                <td className="py-2"><Badge tone={u.is_active ? "bullish" : "bearish"}>{u.is_active ? "yes" : "no"}</Badge></td>
                <td className="py-2 text-xs text-slate-400">{u.last_login_at ? formatRelative(u.last_login_at) : "—"}</td>
                <td className="py-2 text-xs text-slate-400">{formatRelative(u.created_at)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Card>
  );
}
