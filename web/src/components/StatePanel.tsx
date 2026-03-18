"use client";

export default function StatePanel({ loading, error, success, empty }: { loading: boolean; error: string | null; success: string | null; empty: boolean }) {
  if (loading) return <p className="mt-3 text-sm text-warning">Calculating macros and balancing meals…</p>;
  if (error) return <p className="mt-3 text-sm text-destructive">{error}</p>;
  if (empty) return <p className="mt-3 text-sm text-muted-foreground">No planner yet. Generate your first 5-meal day.</p>;
  if (success) return <p className="mt-3 text-sm text-success">{success}</p>;
  return null;
}
