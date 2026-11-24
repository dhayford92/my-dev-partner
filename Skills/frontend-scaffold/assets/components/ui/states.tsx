"use client";
/**
 * Shared state kit — the ONE place for loading/empty/error/skeleton UI.
 * See ../../../../_shared-web/states-and-motion.md.
 */
import * as React from "react";
import { AlertCircleIcon, FolderOpenIcon, InboxIcon, Loader2Icon, type LucideIcon } from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";

export interface EmptyStateProps {
  icon?: LucideIcon | React.ReactNode;
  title: string;
  description?: string;
  action?: { label: string; onClick: () => void };
  className?: string;
}

export function EmptyState({ icon: Icon = InboxIcon, title, description, action, className }: EmptyStateProps) {
  const isElement = React.isValidElement(Icon);
  return (
    <div className={cn("flex flex-col items-center justify-center py-12 text-center", className)}>
      <div className="bg-muted mb-4 flex size-16 items-center justify-center rounded-full">
        {isElement ? (
          <span className="text-muted-foreground">{Icon as React.ReactNode}</span>
        ) : (
          React.createElement(Icon as LucideIcon, { className: "text-muted-foreground size-8" })
        )}
      </div>
      <h3 className="text-lg font-semibold">{title}</h3>
      {description && <p className="text-muted-foreground mt-1 max-w-sm text-sm">{description}</p>}
      {action && (
        <Button onClick={action.onClick} className="mt-4">
          {action.label}
        </Button>
      )}
    </div>
  );
}

export interface LoadingStateProps {
  message?: string;
  variant?: "spinner" | "skeleton" | "dots";
  skeletonCount?: number;
  className?: string;
}

export function LoadingState({ message = "Loading...", variant = "spinner", skeletonCount = 3, className }: LoadingStateProps) {
  if (variant === "skeleton") {
    return (
      <div className={cn("space-y-3", className)}>
        {Array.from({ length: skeletonCount }).map((_, i) => (
          <Skeleton key={i} className="h-20 w-full" />
        ))}
      </div>
    );
  }
  if (variant === "dots") {
    return (
      <div className={cn("flex flex-col items-center justify-center py-12", className)}>
        <div className="flex space-x-1">
          {[0, 1, 2].map((i) => (
            <div key={i} className="bg-primary size-2 animate-bounce rounded-full" style={{ animationDelay: `${i * 0.1}s` }} />
          ))}
        </div>
        {message && <p className="text-muted-foreground mt-4 text-sm">{message}</p>}
      </div>
    );
  }
  return (
    <div className={cn("flex flex-col items-center justify-center py-12", className)}>
      <Loader2Icon className="text-primary size-8 animate-spin" />
      {message && <p className="text-muted-foreground mt-4 text-sm">{message}</p>}
    </div>
  );
}

export interface ErrorStateProps {
  icon?: LucideIcon;
  title?: string;
  description?: string;
  error?: Error | string;
  retry?: { label?: string; onClick: () => void };
  className?: string;
}

export function ErrorState({ icon: Icon = AlertCircleIcon, title = "Something went wrong", description, error, retry, className }: ErrorStateProps) {
  const message = error ? (typeof error === "string" ? error : error.message) : description;
  return (
    <div className={cn("flex flex-col items-center justify-center py-12 text-center", className)}>
      <div className="bg-destructive/10 text-destructive mb-4 flex size-16 items-center justify-center rounded-full">
        <Icon className="size-8" />
      </div>
      <h3 className="text-lg font-semibold">{title}</h3>
      {message && <p className="text-muted-foreground mt-1 max-w-sm text-sm">{message}</p>}
      {retry && (
        <Button variant="outline" onClick={retry.onClick} className="mt-4">
          {retry.label ?? "Try again"}
        </Button>
      )}
    </div>
  );
}

export function NotFoundState({ title = "Not found", description = "The resource you're looking for doesn't exist or has been removed.", action, className }: Omit<EmptyStateProps, "title"> & { title?: string }) {
  return <EmptyState icon={FolderOpenIcon} title={title} description={description} action={action} className={className} />;
}

export function CardSkeleton({ className }: { className?: string }) {
  return (
    <div className={cn("rounded-xl border p-6 space-y-4", className)}>
      <div className="flex items-center justify-between">
        <Skeleton className="h-5 w-32" />
        <Skeleton className="h-8 w-8 rounded-full" />
      </div>
      <Skeleton className="h-4 w-full" />
      <Skeleton className="h-4 w-3/4" />
    </div>
  );
}

export function TableRowSkeleton({ columns = 4, className }: { columns?: number; className?: string }) {
  return (
    <div className={cn("flex items-center gap-4 py-3 px-4", className)}>
      {Array.from({ length: columns }).map((_, i) => (
        <Skeleton key={i} className={cn("h-4", i === 0 ? "w-40" : "w-24", "shrink-0")} />
      ))}
    </div>
  );
}

export function ListSkeleton({ count = 5, className }: { count?: number; className?: string }) {
  return (
    <div className={cn("divide-y rounded-md border", className)}>
      {Array.from({ length: count }).map((_, i) => (
        <TableRowSkeleton key={i} />
      ))}
    </div>
  );
}
