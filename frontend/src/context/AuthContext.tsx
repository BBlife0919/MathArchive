import {
  createContext, useCallback, useContext, useEffect, useState,
  type ReactNode,
} from "react";
import * as authApi from "../api/auth";
import type { User } from "../api/auth";

interface AuthContextValue {
  user: User | null;
  loading: boolean;
  login: (username: string, password: string) => Promise<{ ok: boolean; message: string }>;
  signup: (name: string, username: string, password: string, email: string) => Promise<{ ok: boolean; message: string }>;
  logout: () => Promise<void>;
  refresh: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async () => {
    try {
      const res = await authApi.fetchMe();
      setUser(res.logged_in ? res.user : null);
    } catch {
      setUser(null);
    }
  }, []);

  useEffect(() => {
    refresh().finally(() => setLoading(false));
  }, [refresh]);

  const doLogin = useCallback(async (username: string, password: string) => {
    const res = await authApi.login(username, password);
    if (res.logged_in) {
      setUser(res.user);
      const msg = res.user?.approved
        ? `환영합니다, ${res.user.name}님.`
        : "로그인은 됐지만 아직 관리자 승인 대기 중입니다.";
      return { ok: true, message: msg };
    }
    return { ok: false, message: "아이디 또는 비밀번호가 올바르지 않습니다." };
  }, []);

  const doSignup = useCallback(
    async (name: string, username: string, password: string, email: string) => {
      const res = await authApi.signup(name, username, password, email);
      return { ok: res.ok, message: res.message };
    },
    [],
  );

  const doLogout = useCallback(async () => {
    await authApi.logout();
    setUser(null);
  }, []);

  return (
    <AuthContext.Provider
      value={{ user, loading, login: doLogin, signup: doSignup, logout: doLogout, refresh }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
