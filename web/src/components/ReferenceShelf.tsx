"use client";

export default function ReferenceShelf({ items, saved }: { items: any[]; saved: any[] }) {
  return (
    <div className="grid gap-4 lg:grid-cols-2">
      <div className="rounded-lg border border-border bg-card/80 p-4">
        <h3 className="font-[--font-display] text-lg">Grocery Basket Preview</h3>
        <p className="mt-1 text-sm text-muted-foreground">Auto-grouped produce, proteins, grains, dairy, pantry.</p>
        <ul className="mt-3 space-y-2 text-sm">
          <li>Produce: spinach, berries, broccoli, apples</li>
          <li>Proteins: tofu, eggs, lentils, Greek yogurt</li>
          <li>Grains: quinoa, brown rice, sourdough</li>
        </ul>
      </div>
      <div className="rounded-lg border border-border bg-card/80 p-4">
        <h3 className="font-[--font-display] text-lg">Saved Weekly Planner Pages</h3>
        <div className="mt-3 space-y-2 text-sm">
          {(saved?.length ? saved : items).slice(0, 4).map((s: any, i: number) => (
            <div key={i} className="rounded-md border border-border bg-muted/50 p-2">Plan {i + 1}: {s.summary || "Ava Fat-Loss Monday"}</div>
          ))}
        </div>
      </div>
    </div>
  );
}
