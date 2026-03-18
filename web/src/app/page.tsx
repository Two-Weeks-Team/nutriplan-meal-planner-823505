"use client";
import { useEffect, useState } from "react";
import Hero from "@/components/Hero";
import WorkspacePanel from "@/components/WorkspacePanel";
import InsightPanel from "@/components/InsightPanel";
import CollectionPanel from "@/components/CollectionPanel";
import { fetchItems } from "@/lib/api";

export default function Page() {
  const [folio, setFolio] = useState<{ id: string; name: string; updated_at: string }[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [plan, setPlan] = useState<{ summary: string; items: string[]; score: number } | null>(null);
  const [insights, setInsights] = useState<{ insights: string[]; next_actions: string[]; highlights: string[] } | null>(null);

  const load = async () => {
    setLoading(true);
    setError("");
    try {
      const data = await fetchItems();
      const items = Array.isArray(data) ? data : (data.items ?? []);
      setFolio(items.map((p: Record<string, unknown>) => ({
        id: String(p.id ?? ""),
        name: String(p.name ?? ""),
        updated_at: `${p.goal ?? ""} · ${p.weight_kg ?? ""}kg`,
      })));
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed loading data");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  return (
    <main className="mx-auto max-w-7xl p-4 md:p-6">
      <Hero />
      {error && <div className="mt-3 rounded-md border border-destructive bg-card p-3 text-sm text-destructive">{error}</div>}
      <div className="mt-4 grid gap-4 lg:grid-cols-[1.1fr_1.4fr_1fr]">
        <WorkspacePanel onPlan={setPlan} onError={setError} onInsights={setInsights} />
        {plan ? <InsightPanel summary={plan.summary} items={plan.items} score={plan.score} insights={insights} /> : <section className="rounded-lg border border-border bg-card p-4 text-sm text-muted-foreground">Before you save, generate a complete five-meal day preview.</section>}
        {loading ? <aside className="rounded-lg border border-border bg-card p-4 text-sm">Loading folio…</aside> : <CollectionPanel items={folio} onReload={load} />}
      </div>
    </main>
  );
}
