export type ProcessingStage =
  | "uploaded"
  | "analyzing_video"
  | "generating_report"
  | "completed"
  | "failed";

export type MatchTeamSide = "home" | "away";

export interface Match {
  id: string;
  title: string;
  stage: ProcessingStage;
  error_message: string | null;
  video_url: string;
  annotated_video_url: string | null;
  created_at: string;
  updated_at: string;
}

export interface TeamSplit {
  home: number;
  away: number;
}

export interface PassEdge {
  from_track_id: string;
  to_track_id: string;
  count: number;
}

export interface MomentumPoint {
  time_seconds: number;
  home_possession_pct: number;
  away_possession_pct: number;
}

export interface PassTimelinePoint {
  time_seconds: number;
  count: number;
}

export interface MatchStatistics {
  possession_estimate: TeamSplit;
  average_distance_covered_km: TeamSplit;
  players_tracked: number;
  passing_network: PassEdge[];
  momentum: MomentumPoint[];
  pass_timeline: PassTimelinePoint[];
  passes_by_team: TeamSplit;
  pass_accuracy: TeamSplit;
}

export interface MatchDetail extends Match {
  statistics: MatchStatistics | null;
  report: import("./report").TacticalReport | null;
  players: import("./player").Player[];
}
