const TOKEN_KEY = "luthor_access_token";
const REFRESH_KEY = "luthor_refresh_token";
const EXPIRES_KEY = "luthor_token_expires_at";

export function getAccessToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

export function getRefreshToken(): string | null {
  return localStorage.getItem(REFRESH_KEY);
}

export function getTokenExpiresAt(): number | null {
  const raw = localStorage.getItem(EXPIRES_KEY);
  return raw ? Number(raw) : null;
}

export function setSession(tokens: {
  access_token: string;
  refresh_token?: string | null;
  expires_in?: number | null;
}): void {
  localStorage.setItem(TOKEN_KEY, tokens.access_token);
  if (tokens.refresh_token) {
    localStorage.setItem(REFRESH_KEY, tokens.refresh_token);
  }
  if (tokens.expires_in) {
    const expiresAt = Date.now() + tokens.expires_in * 1000;
    localStorage.setItem(EXPIRES_KEY, String(expiresAt));
  }
}

export function setAccessToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token);
}

export function clearAccessToken(): void {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(REFRESH_KEY);
  localStorage.removeItem(EXPIRES_KEY);
}
