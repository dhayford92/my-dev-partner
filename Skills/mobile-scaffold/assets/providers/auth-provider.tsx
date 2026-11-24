import React, { createContext, useContext, useEffect, useMemo, useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import DataStorage from "@/libs/storage";
import { getAccessToken, logout as logoutAction } from "@/services/actions/auth_actions";

export interface UserModel {
  id: string;
  [key: string]: unknown;
}

export interface AuthContextValue {
  user: UserModel | null;
  isAuthenticated: boolean;
  isHydrated: boolean;
  setUser: (user: UserModel | null) => void;
  signOut: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [isHydrated, setIsHydrated] = useState(false);
  const [user, setUser] = useState<UserModel | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const queryClient = useQueryClient();

  useEffect(() => {
    (async () => {
      try {
        const token = await getAccessToken();
        const cachedUser = await DataStorage.get<UserModel>("user");
        if (token && cachedUser) {
          setUser(cachedUser);
          setIsAuthenticated(true);
        }
      } catch (error) {
        console.error("Auth hydration failed:", error);
      } finally {
        setIsHydrated(true);
      }
    })();
  }, []);

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      isAuthenticated,
      isHydrated,
      setUser: (next) => {
        setUser(next);
        setIsAuthenticated(next != null);
      },
      signOut: async () => {
        queryClient.clear();
        await logoutAction();
        setUser(null);
        setIsAuthenticated(false);
      },
    }),
    [user, isAuthenticated, isHydrated, queryClient],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
