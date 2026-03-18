"use client";

type MealItem = { day?: number; slot?: string; title?: string; prep_minutes?: number; calories?: number; protein_g?: number; carbs_g?: number; fats_g?: number; ingredients?: string[] };
type Props = { summary: string; items: (string | MealItem)[]; score: number; insights: { insights: string[]; next_actions: string[]; highlights: string[] } | null };

export default function InsightPanel({ summary, items, score, insights }: Props) {
  return (
    <section className="rounded-lg border border-border bg-card p-4">
      <h2 className="font-[--font-display] text-xl">Plan Spread</h2>
      <p className="text-sm text-muted-foreground">{summary}</p>
      <p className="mt-2 text-success">Alignment score: {score}</p>
      <div className="mt-3 space-y-2">
        {items.map((item, idx) => {
          if (typeof item === "string") return <p key={idx} className="text-sm">{item}</p>;
          const m = item as MealItem;
          return (
            <div key={idx} className="rounded-md border border-border bg-background/50 p-3">
              <div className="flex items-center justify-between">
                <span className="font-medium">{m.slot ?? `Meal ${idx + 1}`}: {m.title ?? "Untitled"}</span>
                <span className="text-xs text-muted-foreground">{m.calories ?? 0} kcal</span>
              </div>
              <p className="mt-1 text-xs text-muted-foreground">
                P:{m.protein_g ?? 0}g · C:{m.carbs_g ?? 0}g · F:{m.fats_g ?? 0}g · {m.prep_minutes ?? 0}min prep
              </p>
              {m.ingredients && <p className="mt-1 text-xs text-muted-foreground">{m.ingredients.join(", ")}</p>}
            </div>
          );
        })}
      </div>
      {insights && (
        <div className="mt-3 text-sm text-muted-foreground">
          {insights.highlights.join(" • ")}
        </div>
      )}
    </section>
  );
}
