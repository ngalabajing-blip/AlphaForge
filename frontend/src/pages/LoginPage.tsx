import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useAuthStore } from "@/store/auth";

export default function LoginPage() {
  const navigate = useNavigate();

  useEffect(() => {
    useAuthStore.getState().setSession({
      token: "demo-serverless-token",
      user: { id: "demo-user", email: "demo@alphaforge.io", full_name: "Demo User", role: "admin" },
    });
    navigate("/dashboard", { replace: true });
  }, [navigate]);

  return (
    <div className="min-h-screen flex items-center justify-center px-6">
      <div className="glass rounded-2xl px-8 py-9 w-full max-w-sm space-y-4 shadow-xl text-center">
        <h1 className="text-xl font-bold tracking-wide">AlphaForge</h1>
        <p className="text-xs text-slate-400">Redirecting to dashboard...</p>
      </div>
    </div>
  );
}
