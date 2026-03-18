"use client";

export default function FeaturePanel({ planner, onSwap, busy }: { planner: any; onSwap: (slot: string) => void; busy: boolean }) {
  const meals = planner?.items || [
    { slot: "Breakfast", name: "Greek Yogurt Berry Bowl", kcal: 390, ingredients: ["Greek yogurt", "Berries", "Chia"] },
    { slot: "Snack 1", name: "Egg & Avocado Toast", kcal: 280, ingredients: ["Egg", "Avocado", "Sourdough"] },
    { slot: "Lunch", name: "Lentil Quinoa Power Bowl", kcal: 520, ingredients: ["Lentils", "Quinoa", "Spinach"] },
    { slot: "Snack 2", name: "Cottage Cheese + Apple", kcal: 250, ingredients: ["Cottage cheese", "Apple", "Cinnamon"] },
    { slot: "Dinner", name: "Tofu Stir-Fry", kcal: 460, ingredients: ["Tofu", "Broccoli", "Brown rice"] }
  ];

  return (
    <div className="rounded-lg border border-border bg-card/80 p-4 shadow-soft">
      <h2 className="font-[--font-display] text-xl">Five-Meal Daily Planner</h2>
      <div className="mt-3 space-y-3">
        {meals.map((meal: any, idx: number) => (
          <div key={`${meal.slot}-${idx}`} className="rounded-md border border-border bg-muted/60 p-3 transition hover:translate-y-[-1px]">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs text-muted-foreground">{meal.slot}</p>
                <p className="font-medium">{meal.name}</p>
              </div>
              <span className="rounded-full border border-border px-2 py-1 text-xs">{meal.kcal || 400} kcal</span>
            </div>
            <div className="mt-2 flex flex-wrap gap-2">
              {(meal.ingredients || []).map((ing: string) => (
                <span key={ing} className="rounded-full border border-border px-2 py-1 text-xs text-muted-foreground">{ing}</span>
              ))}
            </div>
            <button disabled={busy} onClick={() => onSwap(meal.slot)} className="mt-2 rounded-md bg-accent px-2 py-1 text-xs text-accent-foreground disabled:opacity-60">Swap + Rebalance</button>
          </div>
        ))}
      </div>
    </div>
  );
}
