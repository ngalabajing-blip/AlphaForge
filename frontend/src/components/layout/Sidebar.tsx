import { NavLink } from "react-router-dom";
import clsx from "clsx";

import { useAuthStore } from "@/store/auth";

const navItems: Array<{ to: string; label: string; emoji: string; roles?: string[] }> = [
  { to: "/dashboard", label: "Dashboard", emoji: "📊" },
  { to: "/strategies", label: "Strategies", emoji: "🧠" },
  { to: "/strategies/builder", label: "Strategy Builder", emoji: "🧬" },
  { to: "/backtests", label: "Backtests", emoji: "🧪" },
  { to: "/signals", label: "Signals", emoji: "⚡" },
  { to: "/anomalies", label: "Anomalies", emoji: "🚨" },
  { to: "/alerts", label: "Alerts", emoji: "🔔" },
  { to: "/audits", label: "Audits", emoji: "🛡️" },
  { to: "/admin", label: "Admin", emoji: "🛠", roles: ["admin"] },
  { to: "/settings", label: "Settings", emoji: "⚙" },
];

export const Sidebar = () => {
  const role = useAuthStore((s) => s.user?.role);
  return (
    <aside className="w-60 border-r border-white/10 bg-slate-900/40 px-4 py-5 flex flex-col gap-1">
      <div className="flex items-center gap-2 px-2 mb-4">
        <span className="text-xl">⚒</span>
        <span className="font-bold tracking-wide">AlphaForge</span>
      </div>
      {navItems
        .filter((item) => !item.roles || (role && item.roles.includes(role)))
        .map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.to === "/dashboard"}
            className={({ isActive }) =>
              clsx(
                "flex items-center gap-2 px-2 py-2 rounded-md text-sm",
                isActive
                  ? "bg-primary-600/20 text-white border border-primary-600/40"
                  : "text-slate-300 hover:bg-white/5",
              )
            }
          >
            <span className="text-base">{item.emoji}</span>
            {item.label}
          </NavLink>
        ))}
      <div className="mt-auto text-xs text-slate-500 px-2">
        v0.1.0 · synthetic mode
      </div>
    </aside>
  );
};
