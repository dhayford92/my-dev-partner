import apiFetch from "@/hooks/apiFetch";
import { API_URLS } from "@/libs/api-urls";
import DataStorage, { TokenStorage } from "@/libs/storage";

/**
 * Auth actions. Canonical mobile shape: throw on failure, return data on success — no
 * ActionResult wrapper (mobile has no server/client serialization boundary). See
 * ../../../../_shared-mobile/data-layer.md.
 */

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  expires_in: number;
  token_type?: string;
}

const ACCESS_TOKEN_KEY = "access_token";
const REFRESH_TOKEN_KEY = "refresh_token";
const EXPIRES_IN_KEY = "expires_in";

export async function requestOTP(phoneOrEmail: string): Promise<{ token: string }> {
  return apiFetch<{ token: string }>({
    method: "POST",
    contentType: "application/json",
    url: API_URLS.USERS.AUTH.REQUEST_OTP,
    data: { identifier: phoneOrEmail },
  });
}

export async function verifyOTP(token: string, code: string): Promise<TokenResponse> {
  const response = await apiFetch<TokenResponse>({
    method: "POST",
    contentType: "application/json",
    url: API_URLS.USERS.AUTH.VERIFY_OTP,
    data: { token, code },
  });
  await setAuthData(response);
  return response;
}

export async function logout(): Promise<void> {
  try {
    await apiFetch({ method: "POST", url: API_URLS.USERS.AUTH.LOGOUT, autoAuth: true });
  } finally {
    await clearAuthData();
  }
}

/** Returns null (does not call the endpoint) when no refresh token is stored. */
export async function refreshAccessToken(): Promise<TokenResponse | null> {
  const refreshToken = await TokenStorage.get(REFRESH_TOKEN_KEY);
  if (!refreshToken) return null;
  try {
    const response = await apiFetch<TokenResponse>({
      method: "POST",
      contentType: "application/json",
      url: API_URLS.USERS.AUTH.REFRESH,
      data: { refresh_token: refreshToken },
    });
    await setAuthData(response);
    return response;
  } catch {
    return null;
  }
}

/** Proactive expiry check against a stored absolute timestamp; refreshes if expired. */
export async function getAccessToken(): Promise<string | null> {
  const expiresAt = await DataStorage.get<number>(EXPIRES_IN_KEY);
  const now = Math.floor(Date.now() / 1000);
  if (expiresAt && expiresAt > now) {
    return TokenStorage.get(ACCESS_TOKEN_KEY);
  }
  const refreshed = await refreshAccessToken();
  if (!refreshed) {
    await clearAuthData();
    return null;
  }
  return refreshed.access_token;
}

/** Removes only the auth-related keys — never a blanket storage wipe. */
export async function clearAuthData(): Promise<void> {
  await Promise.allSettled([
    TokenStorage.remove(ACCESS_TOKEN_KEY),
    TokenStorage.remove(REFRESH_TOKEN_KEY),
    DataStorage.remove(EXPIRES_IN_KEY),
    DataStorage.remove("user"),
  ]);
}

export async function setAuthData(tokenResponse: TokenResponse): Promise<void> {
  await TokenStorage.set(ACCESS_TOKEN_KEY, tokenResponse.access_token);
  await TokenStorage.set(REFRESH_TOKEN_KEY, tokenResponse.refresh_token);
  const nowSec = Math.floor(Date.now() / 1000);
  const ttl = Math.max(0, Number(tokenResponse.expires_in) || 0);
  await DataStorage.set(EXPIRES_IN_KEY, nowSec + ttl);
}
