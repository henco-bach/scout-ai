/**
 * Central feature-flag registry.
 *
 * MVP milestones (landing, auth, dashboard, upload, CV pipeline, tactical
 * report, heatmaps) ship enabled. Roadmap features are architected for but
 * stay off until their milestone lands, so the codebase never carries dead
 * UI paths for unshipped work.
 */
export const featureFlags = {
  playerSimilarity: false,
  playerScouting: false,
  transferRecommendations: false,
  formationDetection: false,
  expectedGoals: false,
  expectedThreat: false,
  sprintDetection: false,
  fatigueDetection: false,
  trainingReports: false,
  academyDevelopment: false,
  womensFootballAnalytics: false,
  refereeAnalysis: false,
  aiScout: false,
  aiCoach: false,
  liveMatchAnalysis: false,
} as const;

export type FeatureFlag = keyof typeof featureFlags;

export function isFeatureEnabled(flag: FeatureFlag): boolean {
  return featureFlags[flag];
}
