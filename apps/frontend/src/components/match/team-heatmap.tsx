import type { Player } from "@scout-ai/shared";

const COLS = 20;
const ROWS = 12;
const CELL = 32;

function aggregateHeatmap(players: Player[]): number[][] {
  const grid = Array.from({ length: ROWS }, () => Array<number>(COLS).fill(0));
  for (const player of players) {
    player.heatmap.forEach((row, r) => {
      row.forEach((value, c) => {
        grid[r][c] += value;
      });
    });
  }
  const max = Math.max(1, ...grid.flat());
  return grid.map((row) => row.map((value) => value / max));
}

function TeamHeatmapGrid({ players, color }: { players: Player[]; color: string }) {
  const grid = aggregateHeatmap(players);

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
      <line
        x1={(COLS * CELL) / 2}
        y1={0}
        x2={(COLS * CELL) / 2}
        y2={ROWS * CELL}
        stroke="var(--color-border)"
      />
      {grid.map((row, r) =>
        row.map((value, c) =>
          value > 0 ? (
            <rect
              key={`${r}-${c}`}
              x={c * CELL}
              y={r * CELL}
              width={CELL}
              height={CELL}
              fill={color}
              opacity={Math.min(value, 1) * 0.85}
            />
          ) : null,
        ),
      )}
    </svg>
  );
}

export function TeamHeatmaps({ players }: { players: Player[] }) {
  const home = players.filter((p) => p.team === "home");
  const away = players.filter((p) => p.team === "away");

  return (
    <div className="grid gap-4 sm:grid-cols-2">
      <div>
        <p className="mb-2 text-xs uppercase tracking-wider text-muted-foreground">
          Home Heatmap
        </p>
        <div className="rounded-xl border border-border bg-card p-3">
          <TeamHeatmapGrid players={home} color="var(--color-primary)" />
        </div>
      </div>
      <div>
        <p className="mb-2 text-xs uppercase tracking-wider text-muted-foreground">
          Away Heatmap
        </p>
        <div className="rounded-xl border border-border bg-card p-3">
          <TeamHeatmapGrid players={away} color="var(--color-muted-foreground)" />
        </div>
      </div>
    </div>
  );
}
