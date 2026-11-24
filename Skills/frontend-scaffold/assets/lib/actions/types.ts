/**
 * Server-action envelope + typed API error. Canonical: ActionResult<T> = {data,error}.
 * See ../../../../_shared-web/data-layer.md and api-contract.md.
 */

export type ActionResult<T> =
  | { data: T; error: null }
  | { data: null; error: string };

export const success = <T>(data: T): ActionResult<T> => ({ data, error: null });
export const failure = <T>(error: string): ActionResult<T> => ({ data: null, error });

export function isSuccess<T>(r: ActionResult<T>): r is { data: T; error: null } {
  return r.error === null;
}

export interface FieldError {
  field: string;
  message: string;
}

/**
 * Normalized API error. apiFetch throws this on any non-2xx so callers get a consistent shape
 * regardless of which backend error envelope was returned.
 */
export class ApiError extends Error {
  readonly code: string;
  readonly status: number;
  readonly details?: Record<string, unknown>;
  readonly fieldErrors?: FieldError[];

  constructor(
    message: string,
    code = "UNKNOWN_ERROR",
    status = 500,
    details?: Record<string, unknown>,
    fieldErrors?: FieldError[],
  ) {
    super(message);
    this.name = "ApiError";
    this.code = code;
    this.status = status;
    this.details = details;
    this.fieldErrors = fieldErrors;
  }

  is(code: string): boolean {
    return this.code === code;
  }

  isAuth(): boolean {
    return this.code.startsWith("AUTH_") || this.status === 401 || this.status === 403;
  }

  isRateLimited(): boolean {
    return this.code === "AUTH_RATE_LIMITED" || this.status === 429;
  }
}

/** Extract a user-facing message from anything thrown. */
export function getErrorMessage(error: unknown): string {
  if (error instanceof ApiError || error instanceof Error) return error.message;
  return "An unexpected error occurred";
}
