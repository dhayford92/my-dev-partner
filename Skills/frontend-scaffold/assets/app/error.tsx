"use client";
/** Route-level error boundary for the whole app segment. */
import { useEffect } from "react";
import { ErrorState } from "@/components/ui/states";

export default function Error({ error, reset }: { error: Error & { digest?: string }; reset: () => void }) {
  useEffect(() => {
    console.error(error);
  }, [error]);

  return (
    <div className="flex min-h-[60vh] items-center justify-center p-6">
      <ErrorState
        title="Something went wrong"
        error={error}
        retry={{ label: "Try again", onClick: reset }}
      />
    </div>
  );
}
