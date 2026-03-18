"use client";
import { FormEvent, useMemo, useState } from "react";
import { createPlan, fetchInsights } from "@/lib/api";

type Props = { onPlan: (data: { summary: string; items: string[]; score: number }) => void; onError: (msg: string) => void; onInsights: (data: { insights: string[]; next_actions: string[]; highlights: string[] }) => void };

export default function WorkspacePanel({ onPlan, onError, onInsights }: Props) {
  const [weight, setWeight] = useState("68");
  const [goal, setGoal] = useState("fat loss");
  const [activity, setActivity] = useState("moderate");
  const [diet, setDiet] = useState("high-protein");
  const [restrictions, setRestrictions] = useState("none");
  const [prefs, setPrefs] = useState("asian bowls, mediterranean lunch");
  const [loading, setLoading] = useState(false);

  const query = useMemo(() => `${weight} kg, ${goal}, ${activity} activity, ${diet}, restrictions: ${restrictions}`, [weight, goal, activity, diet, restrictions]);

  const onSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const plan = await createPlan({ query, preferences: prefs });
      onPlan(plan);
      const ins = await fetchInsights("generated-plan", `${query}; ${prefs}`);
      onInsights(ins);
    } catch (err) {
      onError(err instanceof Error ? err.message : "Unexpected error");
    } finally {
      setLoading(false);
    }
  };

  return <form onSubmit={onSubmit} className="rounded-lg border border-border bg-card p-4 shadow-card"><button disabled={loading} className="rounded-md bg-primary px-4 py-2 text-primary-foreground">{loading ? "Generating..." : "Generate Meal Plan"}</button></form>;
}
