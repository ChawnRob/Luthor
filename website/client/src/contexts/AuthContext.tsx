import { clearAccessToken, getAccessToken, setAccessToken } from "@/lib/auth-storage";
import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";

const API_URL = String(import.meta.env.VITE_API_URL ?? "http://localhost:8080").replace(/\/$/, "");

export type UserProfile = {
  id: string;
  email: string;
  name?: string | null;
  quota_tier: string;
  subscription_status: string;
  mfa_enabled: boolean;
  usage: Record<string, number | string>;
};

type AuthContextValue = {
  token: string | null;
  user: UserProfile | null;
  loading: boolean;
  signIn: (email: string, password: string) => Promise<void>;
  signUp: (email: string, password: string, name: string) => Promise<void>;
  signOut: () => void;
  refreshProfile: () => Promise<void>;
};

const AuthContext = createContext<AuthContextValue | null>(null);

async function authRequest<T>(path: string, init?: RequestInit): Promise<T> {
  const headers = new Headers(init?.headers);
  if (init?.body && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }
  const token = getAccessToken();
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const response = await fetch(`${API_URL}${path}`, { ...init, headers });
  if (!response.ok) {
    let detail = response.statusText;
    try {
      const body = await response.json();
      detail = body.detail || detail;
    } catch {
      /* ignore */
    }
    throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
  }
  return response.json() as Promise<T>;
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(() => getAccessToken());
  const [user, setUser] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);

  const refreshProfile = useCallback(async () => {
    const current = getAccessToken();
    if (!current) {
      setUser(null);
      return;
    }
    try {
      const profile = await authRequest<UserProfile>("/auth/me");
      setUser(profile);
    } catch {
      clearAccessToken();
      setToken(null);
      setUser(null);
    }
  }, []);

  useEffect(() => {
    void (async () => {
      setLoading(true);
      await refreshProfile();
      setLoading(false);
    })();
  }, [refreshProfile, token]);

  const signIn = useCallback(async (email: string, password: string) => {
    const result = await authRequest<{ access_token: string }>("/auth/signin", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });
    setAccessToken(result.access_token);
    setToken(result.access_token);
  }, []);

  const signUp = useCallback(async (email: string, password: string, name: string) => {
    const result = await authRequest<{ access_token: string }>("/auth/signup", {
      method: "POST",
      body: JSON.stringify({ email, password, name }),
    });
    setAccessToken(result.access_token);
    setToken(result.access_token);
  }, []);

  const signOut = useCallback(() => {
    clearAccessToken();
    setToken(null);
    setUser(null);
  }, []);

  const value = useMemo(
    () => ({ token, user, loading, signIn, signUp, signOut, refreshProfile }),
    [token, user, loading, signIn, signUp, signOut, refreshProfile],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return ctx;
}
