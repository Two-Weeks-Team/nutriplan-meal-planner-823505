"use client";

export default function StatsStrip({ planner }: { planner: any }) {
  return (
    <div className="grid gap-3 rounded-lg border border-border bg-card/70 p-3 shadow-soft sm:grid-cols-4">
      <div><p className="text-xs text-muted-foreground">Calorie Target</p><p className="text-lg font-semibold">{planner?.score ? Math.round(planner.score * 20 + 1800) : 1900} kcal</p></div>
      <div><p className="text-xs text-muted-foreground">Protein</p><p className="text-lg font-semibold text-primary">132g</p></div>
      <div><p className="text-xs text-muted-foreground">Carbs</p><p className="text-lg font-semibold text-warning">178g</p></div>
      <div><p className="text-xs text-muted-foreground">Fats</p><p className="text-lg font-semibold text-success">63g</p></div>
    </div>
  );
}
