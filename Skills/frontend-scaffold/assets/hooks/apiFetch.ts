/* eslint-disable @typescript-eslint/no-explicit-any */
/**
 * apiFetch — the HTTP client for server actions (NOT a React hook despite living in hooks/).
 * - autoAuth: true pulls the access token from cookies and attaches Bearer.
 * - Throws a normalized ApiError on any non-2xx, parsing all real backend error shapes.
 * See ../../../_shared-web/api-contract.md.
 */

import { ApiError, type FieldError } from "@/lib/actions/types";

export type HttpMethod = "GET" | "POST" | "PUT" | "PATCH" | "DELETE";
export type HttpContentType = "application/json" | "multipart/form-data";

export interface RequestConfig {
  method?: HttpMethod;
  url: string;
  params?: Record<string, string | number | boolean | undefined | null>;
  data?: unknown;
  token?: string;
  contentType?: HttpContentType;
  /** true → fetch the access token from cookies (server actions only). */
  autoAuth?: boolean;
}

function buildQuery(params?: RequestConfig["params"]): string {
  if (!params) return "";
  const sp = new URLSearchParams();
  for (const [k, v] of Object.entries(params)) {
    if (v !== undefined && v !== null) sp.append(k, String(v));
  }
  const s = sp.toString();
  return s ? `?${s}` : "";
}

/**
 * Parse the backend error body into one ApiError. Canonical contract is the FastAPI default
 * { detail } (string; [{loc,msg,type}] for 422) — no machine-code channel, so ApiError.code is
 * derived from the HTTP status; branch on status, show the message. The structured
 * { error: {code,message,details} } branch is kept only to tolerate legacy backends until they migrate.
 */
function normalizeError(status: number, body: any): ApiError {
  // 1. Legacy structured (transitional): { error: { code, message, details } }
  if (body?.error && typeof body.error === "object") {
    const { code, message, details } = body.error;
    const fieldErrors: FieldError[] | undefined = Array.isArray(details?.errors)
      ? details.errors.map((e: any) => ({ field: e.field, message: e.message }))
      : undefined;
    return new ApiError(message ?? "Request failed", code ?? `HTTP_${status}`, status, details, fieldErrors);
  }
  // 2. FastAPI default validation (422): { detail: [{ loc, msg, type }] }
  if (Array.isArray(body?.detail)) {
    const fieldErrors: FieldError[] = body.detail.map((e: any) => ({
      field: Array.isArray(e.loc) ? e.loc.slice(1).join(".") : String(e.loc),
      message: e.msg,
    }));
    return new ApiError("Request validation failed", "VALIDATION_ERROR", status, { errors: body.detail }, fieldErrors);
  }
  // 3. FastAPI default HTTPException (canonical): { detail: "..." }
  if (typeof body?.detail === "string") return new ApiError(body.detail, `HTTP_${status}`, status);
  // 4. Last resort
  return new ApiError(body?.message ?? `Request failed with status ${status}`, `HTTP_${status}`, status);
}

export default async function apiFetch<T>({
  method = "GET",
  url,
  params,
  data,
  token,
  contentType,
  autoAuth = false,
}: RequestConfig): Promise<T> {
  let authToken = token;
  if (autoAuth && !token) {
    try {
      const { getAccessToken } = await import("@/lib/actions/auth");
      authToken = (await getAccessToken()) || undefined;
    } catch {
      /* no token available */
    }
  }

  const headers: Record<string, string> = {};
  if (authToken) headers.Authorization = `Bearer ${authToken}`;

  let sendBody: BodyInit | null = null;
  if (data !== undefined && data !== null) {
    if (contentType === "multipart/form-data") {
      sendBody = data as BodyInit; // let fetch set the boundary
    } else {
      headers["Content-Type"] = "application/json";
      sendBody = JSON.stringify(data);
    }
  }

  let response: Response;
  try {
    response = await fetch(`${url}${buildQuery(params)}`, { method, headers, body: sendBody });
  } catch {
    throw new ApiError("Unable to reach the server. Check your connection and try again.", "NETWORK_ERROR", 0);
  }

  if (response.status === 429) {
    const retryAfter = response.headers.get("Retry-After");
    throw new ApiError(`Rate limit exceeded. Retry after ${retryAfter ?? "some time"}.`, "AUTH_RATE_LIMITED", 429);
  }
  if (response.status === 204) return null as unknown as T;

  const body = await response.json().catch(() => null);
  if (response.ok) return body as T;
  throw normalizeError(response.status, body);
}
