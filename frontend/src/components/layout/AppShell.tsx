import { Outlet } from "react-router-dom";

import { Sidebar } from "@/components/layout/Sidebar";
import { Topbar } from "@/components/layout/Topbar";

export const AppShell = () => (
  <div className="min-h-screen flex bg-slate-950">
    <Sidebar />
    <div className="flex-1 flex flex-col">
      <Topbar />
      <main className="flex-1 px-6 py-6 overflow-auto">
        <Outlet />
      </main>
    </div>
  </div>
);
