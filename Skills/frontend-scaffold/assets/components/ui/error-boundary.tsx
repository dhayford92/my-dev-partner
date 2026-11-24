"use client";
/**
 * Reusable React error boundary for client subtrees that aren't covered by a route error.tsx
 * (e.g. a widget, a chart, a dialog body). Route-level errors use app/error.tsx.
 */
import * as React from "react";
import { ErrorState } from "@/components/ui/states";

interface Props {
  children: React.ReactNode;
  fallback?: (error: Error, reset: () => void) => React.ReactNode;
}
interface State {
  error: Error | null;
}

export class ErrorBoundary extends React.Component<Props, State> {
  state: State = { error: null };

  static getDerivedStateFromError(error: Error): State {
    return { error };
  }

  componentDidCatch(error: Error, info: React.ErrorInfo) {
    // Hook up to Sentry/logging here.
    console.error("ErrorBoundary caught:", error, info.componentStack);
  }

  reset = () => this.setState({ error: null });

  render() {
    if (this.state.error) {
      if (this.props.fallback) return this.props.fallback(this.state.error, this.reset);
      return <ErrorState error={this.state.error} retry={{ onClick: this.reset }} />;
    }
    return this.props.children;
  }
}
