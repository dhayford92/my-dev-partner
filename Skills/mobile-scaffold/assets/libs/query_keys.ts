/**
 * Query key factory — lowercase `queryKeys` export (matches the web suite).
 * Shape per domain: all / list(params?) / detail(id). See ../../../_shared-mobile/data-layer.md.
 */
export const queryKeys = {
  profile: {
    all: ["profile"] as const,
    me: () => [...queryKeys.profile.all, "me"] as const,
  },
  notifications: {
    all: ["notifications"] as const,
    list: () => [...queryKeys.notifications.all, "list"] as const,
  },
  // Template — copy per resource:
  example: {
    all: ["example"] as const,
    list: (params?: Record<string, unknown>) => [...queryKeys.example.all, "list", params] as const,
    detail: (id: string) => [...queryKeys.example.all, "detail", id] as const,
  },
} as const;

export default queryKeys;
