import { useLocation } from "react-router-dom";

import { useAuthStore } from "@/store/auth";

export const ProtectedRoute = ({ children }: { children: JSX.Element }) => {
  const location = useLocation();

  // Serverless demo mode: always auto-login
  const token = useAuthStore((s) => s.token);
  if (!token) {
    useAuthStore.getState().setSession({
      token: "demo-serverless-token",
      user: {
        id: "demo-user",
        email: "demo@alphaforge.io",
        full_name: "Demo User",
        role: "admin",
      },
    });
  }

  return children;
};
