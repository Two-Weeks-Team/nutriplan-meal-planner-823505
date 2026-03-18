"use client";

export default function Hero() {
  return (
    <header className="rounded-lg border border-border bg-card/80 p-5 shadow-folio backdrop-blur">
      <p className="text-xs uppercase tracking-[0.2em] text-muted-foreground">Dietitian Folio</p>
      <h1 className="mt-2 font-[--font-display] text-3xl font-semibold">Nutriplan Meal Planner</h1>
      <p className="mt-2 max-w-2xl text-sm text-muted-foreground">
        AI meal planning that turns your goals into a complete, editable weekly food plan and grocery sheet in one pass.
      </p>
    </header>
  );
}
