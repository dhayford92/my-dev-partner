/**
 * Centralized API endpoints. Base URL from env (never hardcode). Mirrors the backend mount split
 * (/users, /core, /utils) + /api/v1. See ../../../../_shared-web/data-layer.md.
 */

const BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
const VERSION = "v1";

// Cookie namespace so multiple apps on one domain don't collide.
const SLUG = process.env.NEXT_PUBLIC_APP_SLUG ?? "app";
export const ACCESS_TOKEN_COOKIE = `${SLUG}_access_token`;
export const REFRESH_TOKEN_COOKIE = `${SLUG}_refresh_token`;
export const SESSION_COOKIE = `${SLUG}_session`;

export type ApiMount = "users" | "core" | "utils";

export const API_CONFIG = {
  BASE_URL: BASE,
  USERS_BASE: `${BASE}/users/api/${VERSION}`,
  CORE_BASE: `${BASE}/core/api/${VERSION}`,
  UTILS_BASE: `${BASE}/utils/api/${VERSION}`,
} as const;

function base(mount: ApiMount): string {
  return mount === "core" ? API_CONFIG.CORE_BASE : mount === "utils" ? API_CONFIG.UTILS_BASE : API_CONFIG.USERS_BASE;
}

/** Build a full endpoint URL for a given mount. */
export function buildUrl(path: string, mount: ApiMount = "users"): string {
  return `${base(mount)}${path}`;
}

export const AUTH_URLS = {
  LOGIN: buildUrl("/auth/login"),
  LOGOUT: buildUrl("/auth/logout"),
  REFRESH: buildUrl("/auth/refresh"),
  REGISTER: buildUrl("/auth/register"),
  ME: buildUrl("/me"),
} as const;

// Extend per project. Example scaffolded resource group:
export const CORE_URLS = {
  EXAMPLE: {
    LIST: buildUrl("/example", "core"),
    DETAIL: (id: string) => buildUrl(`/example/${id}`, "core"),
  },
} as const;

export const API_URLS = {
  AUTH: AUTH_URLS,
  CORE: CORE_URLS,
} as const;

export default API_URLS;
