import type { MatchStatistics, Player } from "@scout-ai/shared";
import { Percent, Route, Repeat2, Star } from "lucide-react";
import { Sparkline } from "@/components/match/sparkline";

function totalPasses(passingNetwork: MatchStatistics["passing_network"]): number {
  return passingNetwork.reduce((sum, edge) => sum + edge.count, 0);
}

function totalDistance(players: Player[]): number {
  return players.reduce((sum, p) => sum + p.distance_covered_km, 0);
}

function averageRating(players: Player[]): number {
  if (players.length === 0) return 0;
  return players.reduce((sum, p) => sum + p.rating, 0) / players.length;
}

export function KeyInsights({
  statistics,
  players,
}: {
  statistics: MatchStatistics;
  players: Player[];
}) {
  const leader = statistics.possession_estimate.home >= statistics.possession_estimate.away;
  const insights = [
    {
      icon: Percent,
      label: "Possession",
      value: `${Math.round(leader ? statistics.possession_estimate.home : statistics.possession_estimate.away)}%`,
      accent: "text-primary",
      color: "var(--color-primary)",
      series: statistics.momentum.map((p) => p.home_possession_pct),
    },
    {
      icon: Repeat2,
      label: "Total Passes",
      value: totalPasses(statistics.passing_network).toString(),
      accent: "text-sky-400",
      color: "var(--color-sky-400, #38bdf8)",
      series: statistics.pass_timeline.map((p) => p.count),
    },
    {
      icon: Route,
      label: "Total Distance",
      value: `${totalDistance(players).toFixed(1)}km`,
      accent: "text-emerald-400",
      color: "var(--color-emerald-400, #34d399)",
      series: null,
    },
    {
      icon: Star,
      label: "Avg. Rating",
      value: averageRating(players).toFixed(1),
      accent: "text-amber-400",
      color: "var(--color-amber-400, #fbbf24)",
      series: null,
    },
  ];

  return (
    <div>
      <p className="mb-3 text-xs uppercase tracking-wider text-muted-foreground">Key Insights</p>
      <div className="grid grid-cols-2 gap-3">
        {insights.map(({ icon: Icon, label, value, accent, color, series }) => (
          <div key={label} className="rounded-xl border border-border bg-card p-4">
            <Icon className={`size-4 ${accent}`} />
            <p className={`mt-3 font-mono text-xl font-semibold ${accent}`}>{value}</p>
            <p className="mt-1 text-xs text-muted-foreground">{label}</p>
            {series && series.some((v) => v !== 0) && <Sparkline values={series} color={color} />}
          </div>
        ))}
      </div>
    </div>
  );
}
