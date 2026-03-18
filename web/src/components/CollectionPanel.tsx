"use client";

type Props = { items: { id: string; name: string; updated_at: string }[]; onReload: () => void };

export default function CollectionPanel({ items, onReload }: Props) {
  return <aside className="rounded-lg border border-border bg-card p-4"><div className="flex items-center justify-between"><h3 className="font-[--font-display] text-lg">Saved Plan Folio</h3><button onClick={onReload} className="rounded-md bg-muted px-3 py-1 text-xs">Refresh</button></div><ul className="mt-3 space-y-2 text-sm">{items.map((i) => <li key={i.id} className="rounded-md border border-border p-2"><p>{i.name}</p><p className="text-xs text-muted-foreground">Updated {i.updated_at}</p></li>)}</ul></aside>;
}
