"use client";
/** Last-resort boundary that replaces the root layout when it throws. Must render <html>/<body>. */
export default function GlobalError({ error, reset }: { error: Error & { digest?: string }; reset: () => void }) {
  return (
    <html lang="en">
      <body className="flex min-h-screen flex-col items-center justify-center gap-4 p-6 text-center">
        <h1 className="text-xl font-semibold">Something went wrong</h1>
        <p className="text-sm text-neutral-500">{error.message}</p>
        <button
          onClick={reset}
          className="rounded-md border px-4 py-2 text-sm hover:bg-neutral-100"
        >
          Try again
        </button>
      </body>
    </html>
  );
}
