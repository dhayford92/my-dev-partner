export interface FieldError {
  field: string;
  message: string;
}

/** Normalized API error — mirrors the web suite's ApiError shape (see ../../../_shared-web/api-contract.md). */
export class ApiError extends Error {
  readonly status: number;
  readonly fieldErrors?: FieldError[];

  constructor(message: string, status = 500, fieldErrors?: FieldError[]) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.fieldErrors = fieldErrors;
  }

  isAuth(): boolean {
    return this.status === 401 || this.status === 403;
  }
}

export function getErrorMessage(error: unknown): string {
  if (error instanceof Error) return error.message;
  return "An unexpected error occurred";
}
