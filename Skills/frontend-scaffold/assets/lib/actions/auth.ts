"use server";
/**
 * Auth server actions: httpOnly cookie storage + proactive token refresh.
 * Backend token model (see ../../../../_shared-web/api-contract.md + ../../../../_shared-backend/auth.md):
 * JWT HS256, access ~60min, refresh 30d, response { access_token, refresh_token, expires_in }.
 */
import { cookies } from "next/headers";
import { jwtDecode } from "jwt-decode";
import apiFetch from "@/hooks/apiFetch";
import { API_URLS, ACCESS_TOKEN_COOKIE, REFRESH_TOKEN_COOKIE, SESSION_COOKIE } from "@/lib/constants/api-urls";
import { type ActionResult, success, failure, getErrorMessage } from "./types";

interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type?: string;
  expires_in: number;
}

const COOKIE_OPTS = {
  httpOnly: true,
  secure: process.env.NODE_ENV === "production",
  sameSite: "lax" as const,
  path: "/",
};

async function setTokenCookies(t: TokenResponse): Promise<void> {
  const store = await cookies();
  store.set(ACCESS_TOKEN_COOKIE, t.access_token, { ...COOKIE_OPTS, maxAge: t.expires_in });
  store.set(REFRESH_TOKEN_COOKIE, t.refresh_token, { ...COOKIE_OPTS, maxAge: 30 * 24 * 60 * 60 });
  // Non-httpOnly indicator so client code can cheaply know it's signed in.
  store.set(SESSION_COOKIE, "active", { ...COOKIE_OPTS, httpOnly: false, maxAge: 30 * 24 * 60 * 60 });
}

export async function clearTokenCookies(): Promise<void> {
  const store = await cookies();
  store.delete(ACCESS_TOKEN_COOKIE);
  store.delete(REFRESH_TOKEN_COOKIE);
  store.delete(SESSION_COOKIE);
}

export async function getRefreshToken(): Promise<string | null> {
  return (await cookies()).get(REFRESH_TOKEN_COOKIE)?.value ?? null;
}

/**
 * Return a valid access token. Proactively refreshes if the JWT is expired and a refresh token
 * exists; clears cookies if refresh fails. apiFetch({autoAuth:true}) calls this.
 */
export async function getAccessToken(): Promise<string | null> {
  const store = await cookies();
  const access = store.get(ACCESS_TOKEN_COOKIE)?.value;
  if (access) {
    try {
      const { exp } = jwtDecode<{ exp: number }>(access);
      if (exp > Math.floor(Date.now() / 1000) + 5) return access; // 5s skew
    } catch {
      /* fall through to refresh */
    }
  }
  const refresh = store.get(REFRESH_TOKEN_COOKIE)?.value;
  if (!refresh) return null;
  const res = await refreshTokenAction(refresh);
  return res.error ? null : res.data.access_token;
}

export async function loginAction(input: { email: string; password: string }): Promise<ActionResult<TokenResponse>> {
  try {
    const res = await apiFetch<TokenResponse>({
      method: "POST",
      url: API_URLS.AUTH.LOGIN,
      data: input,
      contentType: "application/json",
    });
    await setTokenCookies(res);
    return success(res);
  } catch (error) {
    return failure(getErrorMessage(error));
  }
}

export async function refreshTokenAction(refreshToken?: string): Promise<ActionResult<TokenResponse>> {
  try {
    const token = refreshToken ?? (await getRefreshToken());
    if (!token) return failure("No refresh token");
    const res = await apiFetch<TokenResponse>({
      method: "POST",
      url: API_URLS.AUTH.REFRESH,
      data: { refresh_token: token },
      contentType: "application/json",
    });
    await setTokenCookies(res);
    return success(res);
  } catch (error) {
    await clearTokenCookies();
    return failure(getErrorMessage(error));
  }
}

export async function logoutAction(): Promise<void> {
  try {
    await apiFetch({ method: "POST", url: API_URLS.AUTH.LOGOUT, autoAuth: true });
  } catch {
    /* log out locally regardless */
  }
  await clearTokenCookies();
}

/**
 * Current user. Used by the portal home shell as the first authed-request smoke test.
 * Returns the unwrapped user or throws (so useQuery's isError/isLoading work) — the query-in-
 * useQuery convention from ../../../../_shared-web/data-layer.md. Type this to your real /me response.
 */
export async function getMeAction(): Promise<Record<string, unknown>> {
  return apiFetch<Record<string, unknown>>({ method: "GET", url: API_URLS.AUTH.ME, autoAuth: true });
}
