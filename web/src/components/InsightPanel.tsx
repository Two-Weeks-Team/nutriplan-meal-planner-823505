"use client";

type Props = { summary: string; items: string[]; score: number; insights: { insights: string[]; next_actions: string[]; highlights: string[] } | null };

export default function InsightPanel({ summary, items, score, insights }: Props) {
  return <section className="rounded-lg border border-border bg-card p-4"><h2 className="font-[--font-display] text-xl">Plan Spread</h2><p className="text-sm text-muted-foreground">{summary}</p><p className="mt-2 text-success">Alignment score: {score}</p><ul className="mt-2 list-disc pl-5 text-sm">{items.map((i) => <li key={i}>{i}</li>)}</ul>{insights && <div className="mt-3 text-sm text-muted-foreground">{insights.highlights.join(" • ")}</div>}</section>;
}
