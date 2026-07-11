import type { MomentumPoint } from "@scout-ai/shared";

const WIDTH = 640;
const HEIGHT = 160;
const PADDING = 8;
const CENTER_Y = HEIGHT / 2;

function yFor(homePct: number): number {
  const diff = homePct - 50; // + home momentum, - away momentum
  const scale = (HEIGHT / 2 - PADDING) / 50;
  return CENTER_Y - diff * scale;
}

function buildAreaPath(points: MomentumPoint[]): string {
  if (points.length === 0) return "";
  const stepX = (WIDTH - PADDING * 2) / Math.max(points.length - 1, 1);
  const line = points
    .map((point, i) => {
      const x = PADDING + i * stepX;
      const y = yFor(point.home_possession_pct);
      return `${i === 0 ? "M" : "L"}${x.toFixed(1)},${y.toFixed(1)}`;
    })
    .join(" ");
  const lastX = PADDING + (points.length - 1) * stepX;
  return `${line} L${lastX.toFixed(1)},${CENTER_Y} L${PADDING},${CENTER_Y} Z`;
}

export function MomentumChart({ momentum }: { momentum: MomentumPoint[] }) {
  if (momentum.length === 0) return null;

  const areaPath = buildAreaPath(momentum);

  return (
    <div className="rounded-xl border border-border bg-card p-4">
      <div className="mb-3 flex items-center justify-between">
        <p className="text-xs uppercase tracking-wider text-muted-foreground">Momentum</p>
        <div className="flex items-center gap-4 text-xs text-muted-foreground">
          <span className="flex items-center gap-1.5">
            <span className="size-2 rounded-full bg-primary" /> Home
          </span>
          <span className="flex items-center gap-1.5">
            <span className="size-2 rounded-full bg-rose-400" /> Away
          </span>
        </div>
      </div>
      <svg viewBox={`0 0 ${WIDTH} ${HEIGHT}`} className="w-full">
        <defs>
          <clipPath id="momentum-above">
            <rect x={0} y={0} width={WIDTH} height={CENTER_Y} />
          </clipPath>
          <clipPath id="momentum-below">
            <rect x={0} y={CENTER_Y} width={WIDTH} height={HEIGHT - CENTER_Y} />
          </clipPath>
        </defs>
        <path
          d={areaPath}
          fill="var(--color-primary)"
          fillOpacity={0.25}
          clipPath="url(#momentum-above)"
        />
        <path
          d={areaPath}
          fill="var(--color-rose-400, #fb7185)"
          fillOpacity={0.25}
          clipPath="url(#momentum-below)"
        />
        <path d={areaPath} fill="none" stroke="var(--color-primary)" strokeWidth={1.5} />
        <line
          x1={PADDING}
          y1={CENTER_Y}
          x2={WIDTH - PADDING}
          y2={CENTER_Y}
          stroke="var(--color-border)"
          strokeDasharray="4 4"
        />
      </svg>
      <div className="mt-2 flex justify-between text-xs text-muted-foreground">
        <span>0:00</span>
        <span>{momentum[momentum.length - 1]?.time_seconds.toFixed(0)}s (sampled)</span>
      </div>
    </div>
  );
}
