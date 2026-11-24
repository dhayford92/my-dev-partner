/**
 * Centralized API endpoints. Base URL from EXPO_PUBLIC_API_BASE_URL (set per EAS build profile
 * in eas.json — never hardcode). Mirrors the backend's /users, /core, /utils mount split +
 * /api/v1/{persona}/ shape. See ../../../_shared-mobile/native.md#env-across-build-profiles.
 */

const API_BASE_URL = process.env.EXPO_PUBLIC_API_BASE_URL ?? "http://localhost:8000";
const API_VERSION = "v1";
const PERSONA = "client";

export type ApiApp = "users" | "core" | "utils";

export function getAppBase(app: ApiApp): string {
  switch (app) {
    case "users":
      return `${API_BASE_URL}/users/api/${API_VERSION}/${PERSONA}`;
    case "core":
      return `${API_BASE_URL}/core/api/${API_VERSION}/${PERSONA}`;
    case "utils":
      return `${API_BASE_URL}/utils/api/${API_VERSION}`;
  }
}

export function buildUrl(path: string, app: ApiApp = "users"): string {
  return `${getAppBase(app)}${path}`;
}

export const USERS_URLS = {
  AUTH: {
    REQUEST_OTP: buildUrl("/auth/otp/request"),
    VERIFY_OTP: buildUrl("/auth/otp/verify"),
    REFRESH: buildUrl("/auth/refresh"),
    LOGOUT: buildUrl("/auth/logout"),
  },
  PROFILE: {
    ME: buildUrl("/me"),
    UPDATE_NOTIFICATION_TOKEN: buildUrl("/me/notification-token"),
    DELETE_ACCOUNT: buildUrl("/me/delete"),
  },
} as const;

export const CORE_URLS = {
  // Extend per project.
} as const;

export const UTILS_URLS = {
  NOTIFICATIONS: {
    LIST: buildUrl("/notifications", "utils"),
    MARK_ALL_READ: buildUrl("/notifications/read-all", "utils"),
  },
} as const;

export const API_URLS = {
  USERS: USERS_URLS,
  CORE: CORE_URLS,
  UTILS: UTILS_URLS,
} as const;

export default API_URLS;
