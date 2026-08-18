import { Paginated } from "./types";

const API = "/api/v1";
const ACCESS_KEY = "devflow_access";
const REFRESH_KEY = "devflow_refresh";

let accessToken: string | null = localStorage.getItem(ACCESS_KEY);
let refreshToken: string | null = localStorage.getItem(REFRESH_KEY);

export function hasSession(): boolean {
  return refreshToken !== null;
}

export function setTokens(access: string, refresh: string): void {
  accessToken = access;
  refreshToken = refresh;
  localStorage.setItem(ACCESS_KEY, access);
  localStorage.setItem(REFRESH_KEY, refresh);
}

export function clearTokens(): void {
  accessToken = null;
  refreshToken = null;
  localStorage.removeItem(ACCESS_KEY);
  localStorage.removeItem(REFRESH_KEY);
}

export class ApiError extends Error {
  status: number;
  detail: unknown;

  constructor(status: number, detail: unknown) {
    super(`API error ${status}`);
    this.status = status;
    this.detail = detail;
  }

  /** Primeira mensagem de erro legível retornada pela API. */
  firstMessage(): string {
    const d = this.detail as Record<string, unknown> | string[] | null;
    if (Array.isArray(d)) return String(d[0]);
    if (d && typeof d === "object") {
      const value = Object.values(d)[0];
      if (Array.isArray(value)) return String(value[0]);
      if (value) return String(value);
    }
    return "Algo deu errado. Tente novamente.";
  }
}

async function rawRequest(path: string, options: RequestInit): Promise<Response> {
  const headers: Record<string, string> = {};
  if (options.body) headers["Content-Type"] = "application/json";
  if (accessToken) headers["Authorization"] = `Bearer ${accessToken}`;
  return fetch(`${API}${path}`, { ...options, headers });
}

async function refreshAccess(): Promise<boolean> {
  if (!refreshToken) return false;
  const res = await fetch(`${API}/auth/token/refresh/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh: refreshToken }),
  });
  if (!res.ok) {
    clearTokens();
    return false;
  }
  const data = (await res.json()) as { access: string; refresh?: string };
  setTokens(data.access, data.refresh ?? refreshToken);
  return true;
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  let res = await rawRequest(path, options);
  if (res.status === 401 && (await refreshAccess())) {
    res = await rawRequest(path, options);
  }
  if (!res.ok) {
    let detail: unknown = null;
    try {
      detail = await res.json();
    } catch {
      // resposta sem corpo JSON
    }
    throw new ApiError(res.status, detail);
  }
  if (res.status === 204) return undefined as T;
  return (await res.json()) as T;
}

export const api = {
  get: <T>(path: string) => request<T>(path),
  post: <T>(path: string, body?: unknown) =>
    request<T>(path, { method: "POST", body: body !== undefined ? JSON.stringify(body) : undefined }),
  patch: <T>(path: string, body: unknown) =>
    request<T>(path, { method: "PATCH", body: JSON.stringify(body) }),
  del: (path: string) => request<void>(path, { method: "DELETE" }),
};

/** Busca uma página grande e devolve só os resultados (suficiente para o MVP). */
export async function listAll<T>(path: string): Promise<T[]> {
  const sep = path.includes("?") ? "&" : "?";
  const page = await api.get<Paginated<T>>(`${path}${sep}page_size=200`);
  return page.results;
}

export async function login(username: string, password: string): Promise<void> {
  const res = await fetch(`${API}/auth/token/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });
  if (!res.ok) {
    throw new ApiError(res.status, res.status === 401 ? { detail: "Usuário ou senha inválidos." } : await res.json().catch(() => null));
  }
  const data = (await res.json()) as { access: string; refresh: string };
  setTokens(data.access, data.refresh);
}

export async function registerAccount(payload: {
  username: string;
  email: string;
  password: string;
}): Promise<void> {
  const res = await fetch(`${API}/auth/register/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new ApiError(res.status, await res.json().catch(() => null));
}
