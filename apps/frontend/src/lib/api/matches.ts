import type { Match, MatchDetail, Player } from "@scout-ai/shared";
import { apiClient } from "@/lib/api/client";

export function uploadMatch(
  title: string,
  file: File,
  kickoffOffsetSeconds = 0,
): Promise<Match> {
  const formData = new FormData();
  formData.append("title", title);
  formData.append("file", file);
  formData.append("kickoff_offset_seconds", kickoffOffsetSeconds.toString());
  return apiClient.postForm<Match>("/api/v1/matches", formData);
}

export function renamePlayer(playerId: string, name: string | null): Promise<Player> {
  return apiClient.patch<Player>(`/api/v1/players/${playerId}`, { name });
}

export function listMatches(): Promise<Match[]> {
  return apiClient.get<Match[]>("/api/v1/matches");
}

export function getMatch(id: string): Promise<MatchDetail> {
  return apiClient.get<MatchDetail>(`/api/v1/matches/${id}`);
}

const inProgressStages: MatchDetail["stage"][] = ["uploaded", "analyzing_video", "generating_report"];

export function isMatchProcessing(stage: MatchDetail["stage"]): boolean {
  return inProgressStages.includes(stage);
}
