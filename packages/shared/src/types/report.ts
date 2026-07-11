/**
 * Tactical reports only narrate statistics the computer-vision pipeline
 * already produced — the AI layer must never invent numbers.
 */
export interface TacticalReport {
  summary: string;
  insights: string[];
  recommendations: string[];
  generated_at: string;
  model: string;
}
