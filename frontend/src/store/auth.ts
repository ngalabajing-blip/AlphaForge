import { create } from "zustand";
import { persist } from "zustand/middleware";

export type AuthUser = {
  id: string;
  email: string;
  full_name?: string | null;
  role: "admin" | "researcher" | "viewer" | "service";
};

type AuthState = {
  token: string | null;
  refreshToken: string | null;
  user: AuthUser | null;
  setSession: (data: { token: string; refreshToken?: string; user: AuthUser }) => void;
  clear: () => void;
};

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      token: null,
      refreshToken: null,
      user: null,
      setSession: ({ token, refreshToken, user }) =>
        set({ token, refreshToken: refreshToken ?? null, user }),
      clear: () => set({ token: null, refreshToken: null, user: null }),
    }),
    { name: "alphaforge.auth" },
  ),
);
