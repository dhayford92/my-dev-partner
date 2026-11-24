/* eslint-disable @typescript-eslint/no-explicit-any */
/**
 * apiFetch — the HTTP client for service actions. Adapts the web suite's apiFetch for mobile:
 * no cookies (token comes from expo-secure-store via getAccessToken), otherwise same normalized-
 * error philosophy. See ../../../_shared-mobile/data-layer.md.
 */
import { ApiError, type FieldError } from "@/libs/utils";

export type HttpMethod = "GET" | "POST" | "PUT" | "PATCH" | "DELETE";
export type HttpContentType = "application/json" | "multipart/form-data";

export interface RequestConfig {
  method?: HttpMethod;
  url: string;
  params?: Record<string, string | number | boolean | undefined | null>;
  data?: unknown;
  token?: string;
  contentType?: HttpContentType;
  /** true → fetch the access token from expo-secure-store via getAccessToken(). */
  autoAuth?: boolean;
}

const SUCCESS_STATUS_CODES = new Set([200, 201, 202]);

function buildQuery(params?: RequestConfig["params"]): string {
  if (!params) return "";
  const sp = new URLSearchParams();
  for (const [k, v] of Object.entries(params)) {
    if (v !== undefined && v !== null) sp.append(k, String(v));
  }
  const s = sp.toString();
  return s ? `?${s}` : "";
}

/** Parse the backend's {detail} error body (string, or 422 array of {msg}) into one ApiError. */
function formatApiError(status: number, body: any): ApiError {
  if (typeof body?.detail === "string" && body.detail.trim()) {
    return new ApiError(body.detail.trim(), status);
  }
  if (Array.isArray(body?.detail)) {
    const fieldErrors: FieldError[] = body.detail.map((e: any) => ({
      field: Array.isArray(e.loc) ? e.loc.slice(1).join(".") : String(e.loc ?? ""),
      message: e.msg ?? "Invalid value",
    }));
    const message = fieldErrors.map((f) => f.message).join(". ") || "Validation failed";
    return new ApiError(message, status, fieldErrors);
  }
  if (typeof body?.message === "string") return new ApiError(body.message, status);
  return new ApiError(`Request failed (${status})`, status);
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
      const { getAccessToken } = await import("@/services/actions/auth_actions");
      authToken = (await getAccessToken()) ?? undefined;
    } catch {
      /* no token available */
    }
  }

  const headers: Record<string, string> = {};
  if (authToken) headers.Authorization = `Bearer ${authToken}`;

  let body: BodyInit | null = null;
  if (data !== undefined && data !== null) {
    if (contentType === "multipart/form-data") {
      body = data as BodyInit;
    } else {
      headers["Content-Type"] = "application/json";
      body = JSON.stringify(data);
    }
  }

  const fullUrl = `${url}${buildQuery(params)}`;
  let response: Response;
  try {
    response = await fetch(fullUrl, { method, headers, body });
  } catch {
    throw new ApiError(
      "Cannot reach the server. Check your connection and try again.",
      0,
    );
  }

  if (response.status === 429) {
    const retryAfter = response.headers.get("Retry-After");
    throw new ApiError(`Rate limit exceeded. Retry after ${retryAfter ?? "some time"}.`, 429);
  }
  if (response.status === 204) return null as unknown as T;

  const rawText = await response.text();
  let result: any = null;
  if (rawText) {
    try {
      result = JSON.parse(rawText);
    } catch {
      result = rawText;
    }
  }

  if (SUCCESS_STATUS_CODES.has(response.status)) return result as T;

  if (__DEV__) {
    console.warn(`[apiFetch] ${response.status} ${fullUrl}`, result);
  }
  throw formatApiError(response.status, result);
}
