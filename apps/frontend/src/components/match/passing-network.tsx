import type { PassEdge, Player } from "@scout-ai/shared";

const COLS = 20;
const ROWS = 12;
const CELL = 32;

function PitchNetwork({ players, edges, color }: { players: Player[]; edges: PassEdge[]; color: string }) {
  const byTrackId = new Map(players.map((p) => [p.track_id, p]));
  const maxCount = Math.max(1, ...edges.map((e) => e.count));

  return (
    <svg viewBox={`0 0 ${COLS * CELL} ${ROWS * CELL}`} className="w-full">
      <rect
        x={1}
        y={1}
        width={COLS * CELL - 2}
        height={ROWS * CELL - 2}
        fill="none"
        stroke="var(--color-border)"
      />
      {edges.map((edge) => {
        const from = byTrackId.get(edge.from_track_id);
        const to = byTrackId.get(edge.to_track_id);
        if (!from || !to) return null;
        return (
          <line
            key={`${edge.from_track_id}-${edge.to_track_id}`}
            x1={from.average_position.x * COLS * CELL}
            y1={from.average_position.y * ROWS * CELL}
            x2={to.average_position.x * COLS * CELL}
            y2={to.average_position.y * ROWS * CELL}
            stroke={color}
            strokeWidth={1 + (edge.count / maxCount) * 3}
            opacity={0.6}
          />
        );
      })}
      {players.map((player) => (
        <circle
          key={player.id}
          cx={player.average_position.x * COLS * CELL}
          cy={player.average_position.y * ROWS * CELL}
          r={5}
          fill={color}
        />
      ))}
    </svg>
  );
}

export function PassingNetwork({
  players,
  passingNetwork,
}: {
  players: Player[];
  passingNetwork: PassEdge[];
}) {
  const home = players.filter((p) => p.team === "home");
  const away = players.filter((p) => p.team === "away");
  const homeIds = new Set(home.map((p) => p.track_id));
  const homeEdges = passingNetwork.filter((e) => homeIds.has(e.from_track_id));
  const awayEdges = passingNetwork.filter((e) => !homeIds.has(e.from_track_id));

  if (passingNetwork.length === 0) {
    return (
      <p className="text-sm text-muted-foreground">
        No passes were detected in this match — either possession changed teams too quickly to
        track, or too few players stayed on-screen long enough to link together.
      </p>
    );
  }

  return (
    <div className="grid gap-4 sm:grid-cols-2">
      <div>
        <p className="mb-2 text-xs uppercase tracking-wider text-muted-foreground">
          Home Passing Network
        </p>
        <div className="rounded-xl border border-border bg-card p-3">
          <PitchNetwork players={home} edges={homeEdges} color="var(--color-primary)" />
        </div>
      </div>
      <div>
        <p className="mb-2 text-xs uppercase tracking-wider text-muted-foreground">
          Away Passing Network
        </p>
        <div className="rounded-xl border border-border bg-card p-3">
          <PitchNetwork players={away} edges={awayEdges} color="var(--color-muted-foreground)" />
        </div>
      </div>
    </div>
  );
}
