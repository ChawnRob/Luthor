import {
  clearAccessToken,
  getAccessToken,
  getRefreshToken,
  getTokenExpiresAt,
  setSession,
} from "@/lib/auth-storage";
import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
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

type AuthTokens = {
  access_token: string;
  refresh_token?: string | null;
  expires_in?: number | null;
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
  const refreshTimer = useRef<number | null>(null);

  const refreshSession = useCallback(async () => {
    const refreshToken = getRefreshToken();
    if (!refreshToken) {
      return false;
    }
    try {
      const result = await authRequest<AuthTokens>("/auth/refresh", {
        method: "POST",
        body: JSON.stringify({ refresh_token: refreshToken }),
      });
      setSession(result);
      setToken(result.access_token);
      return true;
    } catch {
      return false;
    }
  }, []);

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
      const renewed = await refreshSession();
      if (!renewed) {
        clearAccessToken();
        setToken(null);
        setUser(null);
        return;
      }
      const profile = await authRequest<UserProfile>("/auth/me");
      setUser(profile);
    }
  }, [refreshSession]);

  const scheduleRefresh = useCallback(() => {
    if (refreshTimer.current) {
      window.clearTimeout(refreshTimer.current);
    }
    const expiresAt = getTokenExpiresAt();
    if (!expiresAt || !getRefreshToken()) {
      return;
    }
    const delay = Math.max(expiresAt - Date.now() - 60_000, 5_000);
    refreshTimer.current = window.setTimeout(() => {
      void refreshSession().then((ok) => {
        if (ok) {
          void refreshProfile();
          scheduleRefresh();
        }
      });
    }, delay);
  }, [refreshSession, refreshProfile]);

  useEffect(() => {
    void (async () => {
      setLoading(true);
      await refreshProfile();
      scheduleRefresh();
      setLoading(false);
    })();
    return () => {
      if (refreshTimer.current) {
        window.clearTimeout(refreshTimer.current);
      }
    };
  }, [refreshProfile, scheduleRefresh, token]);

  const persistTokens = useCallback((result: AuthTokens) => {
    setSession(result);
    setToken(result.access_token);
    scheduleRefresh();
  }, [scheduleRefresh]);

  const signIn = useCallback(async (email: string, password: string) => {
    const result = await authRequest<AuthTokens>("/auth/signin", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });
    persistTokens(result);
  }, [persistTokens]);

  const signUp = useCallback(async (email: string, password: string, name: string) => {
    const result = await authRequest<AuthTokens>("/auth/signup", {
      method: "POST",
      body: JSON.stringify({ email, password, name }),
    });
    persistTokens(result);
  }, [persistTokens]);

  const signOut = useCallback(() => {
    clearAccessToken();
    setToken(null);
    setUser(null);
    if (refreshTimer.current) {
      window.clearTimeout(refreshTimer.current);
    }
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
