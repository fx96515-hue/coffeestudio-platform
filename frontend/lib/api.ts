export type Token = {
  access_token: string;
  token_type?: string;
  expires_in?: number;
};

type ApiFetchOptions = RequestInit & {
  /** If true, do not attach Authorization header */
  skipAuth?: boolean;
};

const TOKEN_KEY = "token";

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  const v = window.localStorage.getItem(TOKEN_KEY);
  return v && v.trim() ? v : null;
}

export function setToken(token?: string | null) {
  if (typeof window === "undefined") return;
  const t = (token || "").trim();
  if (!t) {
    window.localStorage.removeItem(TOKEN_KEY);
    return;
  }
  window.localStorage.setItem(TOKEN_KEY, t);
}

export function apiBaseUrl(): string {
  const env = process.env.NEXT_PUBLIC_API_URL;
  if (env) return env;

  if (typeof window === "undefined") return "http://localhost:8000";

  // If UI served via Traefik hostname, use Traefik API hostname too
  if (window.location.hostname === "ui.localhost") return "http://api.localhost";

  // Fallback (direct port)
  return "http://localhost:8000";
}

export async function apiFetch<T = any>(path: string, options: ApiFetchOptions = {}): Promise<T> {
  const { skipAuth, ...req } = options;

  const token = !skipAuth ? getToken() : null;

  const headers: Record<string, string> = {
    ...(req.headers as Record<string, string>),
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };

  // auto JSON content-type when body is string and not set
  if (req.body && typeof req.body === "string" && !headers["Content-Type"]) {
    headers["Content-Type"] = "application/json";
  }

  const base = apiBaseUrl();
  const url = `${base}${path}`;

  const tryFetch = async (u: string) => {
    const res = await fetch(u, { ...req, headers });
    if (!res.ok) {
      const txt = await res.text().catch(() => "");
      throw new Error(`API error: ${res.status} ${txt}`.trim());
    }
    const ct = res.headers.get("content-type") || "";
    if (ct.includes("application/json")) return (await res.json()) as T;
    return (await res.text()) as unknown as T;
  };

  try {
    return await tryFetch(url);
  } catch (e) {
    // fallback: if traefik host fails, try direct backend port
    if (base.includes("api.localhost")) {
      return await tryFetch(`http://localhost:8000${path}`);
    }
    throw e;
  }
}
