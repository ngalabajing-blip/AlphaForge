import { useState } from "react";
import { useNavigate } from "react-router-dom";

import api from "@/lib/api";
import { useAuthStore } from "@/store/auth";
import { Spinner } from "@/components/ui/Spinner";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();
  const setSession = useAuthStore((s) => s.setSession);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const tokenResp = await api.postForm("/auth/token", { username: email, password });
      const token = tokenResp.data.access_token as string;
      const meResp = await api.get("/users/me", { headers: { Authorization: `Bearer ${token}` } });
      setSession({ token, refreshToken: tokenResp.data.refresh_token, user: meResp.data });
      navigate("/dashboard");
    } catch (err: any) {
      setError(err?.response?.data?.detail || "Login failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-6">
      <form onSubmit={handleSubmit} className="glass rounded-2xl px-8 py-9 w-full max-w-sm space-y-4 shadow-xl">
        <div className="space-y-1 text-center">
          <h1 className="text-xl font-bold tracking-wide">AlphaForge</h1>
          <p className="text-xs text-slate-400">Algorithmic trading & on-chain intelligence</p>
        </div>
        <label className="block">
          <span className="text-xs text-slate-400">Email</span>
          <input
            type="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="mt-1 w-full bg-slate-900 border border-white/10 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
        </label>
        <label className="block">
          <span className="text-xs text-slate-400">Password</span>
          <input
            type="password"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="mt-1 w-full bg-slate-900 border border-white/10 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
        </label>
        {error && <div className="text-rose-400 text-xs">{error}</div>}
        <button type="submit" className="btn-primary w-full" disabled={loading}>
          {loading ? <Spinner /> : "Sign in"}
        </button>
        <p className="text-xs text-slate-500 text-center">
          Don't have an account? Ask an admin to create one.
        </p>
      </form>
    </div>
  );
}
