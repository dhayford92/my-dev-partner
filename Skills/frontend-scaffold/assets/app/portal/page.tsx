"use client";
import { useQuery } from "@tanstack/react-query";
import { LoadingState, ErrorState } from "@/components/ui/states";
import { getMeAction } from "@/lib/actions/auth";
import { queryKeys } from "@/lib/constants/query-keys";
import { getErrorMessage } from "@/lib/actions/types";

/**
 * Portal home shell + first-run smoke test: renders, then makes one authenticated request via a
 * server action and surfaces loading / error / data using the shared states kit.
 */
export default function PortalHome() {
  const meQuery = useQuery({
    queryKey: queryKeys.profile.me(),
    queryFn: getMeAction,
    retry: false,
  });

  return (
    <section className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Welcome</h1>
        <p className="text-muted-foreground text-sm">Your authenticated shell is rendering.</p>
      </div>

      <div className="rounded-xl border p-6">
        <h2 className="mb-3 text-sm font-semibold">Backend connection</h2>
        {meQuery.isLoading ? (
          <LoadingState variant="skeleton" skeletonCount={2} />
        ) : meQuery.isError ? (
          <ErrorState
            title="Could not reach the API"
            error={getErrorMessage(meQuery.error)}
            retry={{ onClick: () => meQuery.refetch() }}
          />
        ) : (
          <pre className="text-muted-foreground overflow-x-auto text-xs">
            {JSON.stringify(meQuery.data, null, 2)}
          </pre>
        )}
      </div>
    </section>
  );
}
