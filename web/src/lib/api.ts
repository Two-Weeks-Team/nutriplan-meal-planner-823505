export type PlanRequest = { query: string; preferences: string };

export async function fetchItems() {
  const res = await fetch("/api/items", { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to load starter folio");
  return res.json();
}

export async function createPlan(payload: PlanRequest) {
  const res = await fetch("/api/plan", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  if (!res.ok) throw new Error("Plan generation failed");
  return res.json() as Promise<{ summary: string; items: string[]; score: number }>;
}

export async function fetchInsights(selection: string, context: string) {
  const res = await fetch("/api/insights", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ selection, context })
  });
  if (!res.ok) throw new Error("Could not compute insights");
  return res.json() as Promise<{ insights: string[]; next_actions: string[]; highlights: string[] }>;
}
