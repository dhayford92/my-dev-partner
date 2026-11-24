/**
 * Query key factory — the single source for cache keys. Every useQuery/invalidateQueries goes
 * through this; never inline string arrays. Shape per domain: all / list(params) / detail(id).
 * See ../../../../_shared-web/data-layer.md.
 */
export const queryKeys = {
  auth: {
    all: ["auth"] as const,
    session: () => [...queryKeys.auth.all, "session"] as const,
  },
  profile: {
    all: ["profile"] as const,
    me: () => [...queryKeys.profile.all, "me"] as const,
  },
  // Template — copy per resource:
  example: {
    all: ["example"] as const,
    list: (params?: Record<string, unknown>) => [...queryKeys.example.all, "list", params] as const,
    detail: (id: string) => [...queryKeys.example.all, "detail", id] as const,
  },
} as const;

export default queryKeys;
