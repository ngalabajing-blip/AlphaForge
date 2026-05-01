import { useAuthStore } from "@/store/auth";

export const Topbar = () => {
  const user = useAuthStore((s) => s.user);
  const clear = useAuthStore((s) => s.clear);
  return (
    <header className="h-14 px-6 border-b border-white/10 flex items-center justify-between bg-slate-900/30">
      <div className="text-sm text-slate-400">
        Welcome back, <span className="text-slate-200">{user?.full_name || user?.email}</span>
      </div>
      <div className="flex items-center gap-3">
        <span className="text-xs text-slate-500 uppercase">{user?.role}</span>
        <button className="btn-ghost" onClick={() => clear()}>
          Sign out
        </button>
      </div>
    </header>
  );
};
