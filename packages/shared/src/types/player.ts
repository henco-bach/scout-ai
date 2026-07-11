import type { MatchTeamSide } from "./match";

export interface Position {
  x: number;
  y: number;
}

export interface Player {
  id: string;
  team: MatchTeamSide;
  track_id: string;
  name: string | null;
  average_position: Position;
  distance_covered_km: number;
  /** Normalized 0-1 pitch-space grid of visit density. */
  heatmap: number[][];
  touches: number;
  passes_made: number;
  passes_received: number;
  /** Composite score (3-10) from relative distance, touches, and passes — not a subjective rating. */
  rating: number;
}
