import type { MatchStatistics } from "@scout-ai/shared";
import { Card, CardContent } from "@/components/ui/card";

function TeamSplitCard({
  label,
  home,
  away,
  barPct,
}: {
  label: string;
  home: string;
  away: string;
  barPct?: number;
}) {
  return (
    <Card>
      <CardContent>
        <p className="text-xs uppercase tracking-wider text-muted-foreground">{label}</p>
        <div className="mt-3 flex items-end justify-between font-mono">
          <span className="text-2xl font-semibold text-primary">{home}</span>
          <span className="text-xs text-muted-foreground">vs</span>
          <span className="text-2xl font-semibold">{away}</span>
        </div>
        {barPct !== undefined && (
          <div className="mt-3 h-1.5 overflow-hidden rounded-full bg-muted">
            <div className="h-full bg-primary" style={{ width: `${barPct}%` }} />
          </div>
        )}
        <div className="mt-1.5 flex justify-between text-xs text-muted-foreground">
          <span>Home</span>
          <span>Away</span>
        </div>
      </CardContent>
    </Card>
  );
}

export function StatCards({ statistics }: { statistics: MatchStatistics }) {
  const {
    possession_estimate,
    average_distance_covered_km,
    players_tracked,
    passes_by_team,
    pass_accuracy,
  } = statistics;

  const hasPassStats = passes_by_team.home + passes_by_team.away > 0;

  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      <TeamSplitCard
        label="Possession Estimate"
        home={`${possession_estimate.home.toFixed(0)}%`}
        away={`${possession_estimate.away.toFixed(0)}%`}
        barPct={possession_estimate.home}
      />

      <TeamSplitCard
        label="Avg. Distance Covered"
        home={`${average_distance_covered_km.home.toFixed(1)}km`}
        away={`${average_distance_covered_km.away.toFixed(1)}km`}
      />

      <Card>
        <CardContent>
          <p className="text-xs uppercase tracking-wider text-muted-foreground">Players Tracked</p>
          <p className="mt-3 font-mono text-2xl font-semibold">{players_tracked}</p>
          <p className="mt-4 text-xs text-muted-foreground">Detected via YOLO + ByteTrack</p>
        </CardContent>
      </Card>

      {hasPassStats && (
        <>
          <TeamSplitCard
            label="Passes by Team"
            home={passes_by_team.home.toString()}
            away={passes_by_team.away.toString()}
            barPct={(passes_by_team.home / (passes_by_team.home + passes_by_team.away)) * 100}
          />

          <TeamSplitCard
            label="Pass Accuracy"
            home={`${pass_accuracy.home.toFixed(0)}%`}
            away={`${pass_accuracy.away.toFixed(0)}%`}
          />
        </>
      )}
    </div>
  );
}
