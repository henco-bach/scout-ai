"use client";

import { use } from "react";
import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { AlertTriangle, ArrowLeft } from "lucide-react";
import { DashboardShell } from "@/components/dashboard/dashboard-shell";
import { ProcessingStatus } from "@/components/match/processing-status";
import { StatCards } from "@/components/match/stat-cards";
import { TeamHeatmaps } from "@/components/match/team-heatmap";
import { TacticalReportCard } from "@/components/match/tactical-report-card";
import { MomentumChart } from "@/components/match/momentum-chart";
import { PassingNetwork } from "@/components/match/passing-network";
import { PlayerStatsTable } from "@/components/match/player-stats-table";
import { KeyInsights } from "@/components/match/key-insights";
import { TopPlayers } from "@/components/match/top-players";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { getMatch, isMatchProcessing } from "@/lib/api/matches";
import { env } from "@/config/env";

export default function MatchPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);

  const {
    data: match,
    isLoading,
    isError,
  } = useQuery({
    queryKey: ["match", id],
    queryFn: () => getMatch(id),
    refetchInterval: (query) =>
      query.state.data && !isMatchProcessing(query.state.data.stage) ? false : 2000,
  });

  return (
    <DashboardShell>
      <div className="mx-auto w-full max-w-7xl px-6 py-10">
        <Link
          href="/matches"
          className="mb-6 inline-flex items-center gap-1.5 text-sm text-muted-foreground hover:text-foreground"
        >
          <ArrowLeft className="size-4" />
          All matches
        </Link>

        {isError ? (
          <Card>
            <CardContent className="flex flex-col items-center gap-3 py-12 text-center">
              <AlertTriangle className="size-8 text-destructive" strokeWidth={1.5} />
              <p className="text-muted-foreground">
                Couldn&apos;t load this match. Check the backend is running and try again.
              </p>
            </CardContent>
          </Card>
        ) : isLoading || !match ? (
          <div className="flex flex-col gap-4">
            <Skeleton className="h-8 w-64" />
            <Skeleton className="h-64 w-full" />
          </div>
        ) : (
          <div className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_320px]">
            <div className="flex flex-col gap-6">
              <div className="flex flex-wrap items-center gap-3">
                <h1 className="font-heading text-2xl font-semibold tracking-tight">
                  {match.title}
                </h1>
                <Badge
                  variant="outline"
                  className={
                    match.stage === "completed"
                      ? "border-primary/40 text-primary"
                      : match.stage === "failed"
                        ? "border-destructive/40 text-destructive"
                        : "text-muted-foreground"
                  }
                >
                  {match.stage === "completed" ? "Completed" : match.stage.replaceAll("_", " ")}
                </Badge>
                <span className="text-xs text-muted-foreground">
                  {new Date(match.created_at).toLocaleDateString(undefined, {
                    year: "numeric",
                    month: "long",
                    day: "numeric",
                  })}
                </span>
              </div>

              <ProcessingStatus stage={match.stage} errorMessage={match.error_message} />

              <video
                controls
                className="max-h-[60vh] w-full rounded-xl border border-border bg-black object-contain"
                src={`${env.NEXT_PUBLIC_API_URL}${match.annotated_video_url ?? match.video_url}`}
              />

              {match.statistics && (
                <Tabs defaultValue="overview">
                  <TabsList>
                    <TabsTrigger value="overview">Overview</TabsTrigger>
                    <TabsTrigger value="heatmaps">Heatmaps</TabsTrigger>
                    <TabsTrigger value="passing">Passing Network</TabsTrigger>
                    <TabsTrigger value="players">Player Stats</TabsTrigger>
                  </TabsList>

                  <TabsContent value="overview" className="flex flex-col gap-4">
                    {match.players.length > 0 && <TopPlayers players={match.players} />}
                    <StatCards statistics={match.statistics} />
                    <MomentumChart momentum={match.statistics.momentum} />
                  </TabsContent>

                  <TabsContent value="heatmaps">
                    {match.players.length > 0 ? (
                      <TeamHeatmaps players={match.players} />
                    ) : (
                      <p className="text-sm text-muted-foreground">No players tracked to map.</p>
                    )}
                  </TabsContent>

                  <TabsContent value="passing">
                    <PassingNetwork
                      players={match.players}
                      passingNetwork={match.statistics.passing_network}
                    />
                  </TabsContent>

                  <TabsContent value="players">
                    {match.players.length > 0 ? (
                      <PlayerStatsTable matchId={id} players={match.players} />
                    ) : (
                      <p className="text-sm text-muted-foreground">No players tracked.</p>
                    )}
                  </TabsContent>
                </Tabs>
              )}
            </div>

            {match.statistics && (
              <div className="flex flex-col gap-6">
                <KeyInsights statistics={match.statistics} players={match.players} />
                {match.report && <TacticalReportCard report={match.report} />}
              </div>
            )}
          </div>
        )}
      </div>
    </DashboardShell>
  );
}
