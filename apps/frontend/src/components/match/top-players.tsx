import type { Player } from "@scout-ai/shared";

export function TopPlayers({ players }: { players: Player[] }) {
  const top = [...players].sort((a, b) => b.rating - a.rating).slice(0, 3);

  if (top.length === 0) return null;

  return (
    <div className="rounded-xl border border-border bg-card p-4">
      <p className="mb-3 text-xs uppercase tracking-wider text-muted-foreground">Top Players</p>
      <div className="flex flex-col gap-1">
        {top.map((player, i) => (
          <div key={player.id} className="flex items-center gap-3 rounded-lg px-2 py-2">
            <span className="w-4 text-sm text-muted-foreground">{i + 1}</span>
            <span
              className={`flex size-7 shrink-0 items-center justify-center rounded-full text-xs font-semibold ${
                player.team === "home"
                  ? "bg-primary/20 text-primary"
                  : "bg-muted-foreground/20 text-muted-foreground"
              }`}
            >
              {player.track_id}
            </span>
            <span className="flex-1 text-sm font-medium">
              {player.name ?? `${player.team === "home" ? "Home" : "Away"} #${player.track_id}`}
            </span>
            <span className="rounded-md border border-primary/40 px-2 py-0.5 font-mono text-xs font-semibold text-primary">
              {player.rating.toFixed(1)}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
