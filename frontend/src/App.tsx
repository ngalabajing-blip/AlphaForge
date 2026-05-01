import { Navigate, Route, Routes } from "react-router-dom";
import { lazy, Suspense } from "react";

import { AppShell } from "@/components/layout/AppShell";
import { ProtectedRoute } from "@/components/auth/ProtectedRoute";
import LoginPage from "@/pages/LoginPage";
import DashboardPage from "@/pages/DashboardPage";

const StrategiesPage = lazy(() => import("@/pages/StrategiesPage"));
const StrategyBuilderPage = lazy(() => import("@/pages/StrategyBuilderPage"));
const BacktestsPage = lazy(() => import("@/pages/BacktestsPage"));
const BacktestDetailPage = lazy(() => import("@/pages/BacktestDetailPage"));
const SignalsPage = lazy(() => import("@/pages/SignalsPage"));
const AnomalyPage = lazy(() => import("@/pages/AnomalyPage"));
const AlertsPage = lazy(() => import("@/pages/AlertsPage"));
const AuditsPage = lazy(() => import("@/pages/AuditsPage"));
const AuditDetailPage = lazy(() => import("@/pages/AuditDetailPage"));
const AdminPage = lazy(() => import("@/pages/AdminPage"));
const SettingsPage = lazy(() => import("@/pages/SettingsPage"));

const Loading = () => (
  <div className="p-10 text-slate-400 text-sm">Loading…</div>
);

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route element={<ProtectedRoute><AppShell /></ProtectedRoute>}>
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/strategies" element={<Suspense fallback={<Loading />}><StrategiesPage /></Suspense>} />
        <Route path="/strategies/builder/:id?" element={<Suspense fallback={<Loading />}><StrategyBuilderPage /></Suspense>} />
        <Route path="/backtests" element={<Suspense fallback={<Loading />}><BacktestsPage /></Suspense>} />
        <Route path="/backtests/:id" element={<Suspense fallback={<Loading />}><BacktestDetailPage /></Suspense>} />
        <Route path="/signals" element={<Suspense fallback={<Loading />}><SignalsPage /></Suspense>} />
        <Route path="/anomalies" element={<Suspense fallback={<Loading />}><AnomalyPage /></Suspense>} />
        <Route path="/alerts" element={<Suspense fallback={<Loading />}><AlertsPage /></Suspense>} />
        <Route path="/audits" element={<Suspense fallback={<Loading />}><AuditsPage /></Suspense>} />
        <Route path="/audits/:id" element={<Suspense fallback={<Loading />}><AuditDetailPage /></Suspense>} />
        <Route path="/admin" element={<Suspense fallback={<Loading />}><AdminPage /></Suspense>} />
        <Route path="/settings" element={<Suspense fallback={<Loading />}><SettingsPage /></Suspense>} />
      </Route>
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
}
