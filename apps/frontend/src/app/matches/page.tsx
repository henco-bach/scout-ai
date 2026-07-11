"use client";

import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { Video, ArrowRight, AlertTriangle } from "lucide-react";
import { DashboardShell } from "@/components/dashboard/dashboard-shell";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { ProcessingStatus } from "@/components/match/processing-status";
import { listMatches } from "@/lib/api/matches";

export default function MatchesPage() {
  const {
    data: matches,
    isLoading,
    isError,
  } = useQuery({
    queryKey: ["matches"],
    queryFn: listMatches,
  });

  return (
    <DashboardShell>
      <div className="mx-auto w-full max-w-3xl px-6 py-10">
        <div className="mb-8 flex items-center justify-between">
          <h1 className="font-heading text-2xl font-semibold tracking-tight">Analyses</h1>
          <Button size="sm" nativeButton={false} render={<Link href="/upload" />}>
            Upload Match
          </Button>
        </div>

        {isLoading && (
          <div className="flex flex-col gap-3">
            <Skeleton className="h-20 w-full" />
            <Skeleton className="h-20 w-full" />
          </div>
        )}

        {isError && (
          <Card>
            <CardContent className="flex flex-col items-center gap-3 py-12 text-center">
              <AlertTriangle className="size-8 text-destructive" strokeWidth={1.5} />
              <p className="text-muted-foreground">
                Couldn&apos;t reach the backend. Check it&apos;s running and try again.
              </p>
            </CardContent>
          </Card>
        )}

        {!isLoading && !isError && matches?.length === 0 && (
          <Card>
            <CardContent className="flex flex-col items-center gap-3 py-12 text-center">
              <Video className="size-8 text-muted-foreground" strokeWidth={1.5} />
              <p className="text-muted-foreground">No matches analyzed yet.</p>
              <Button nativeButton={false} render={<Link href="/upload" />}>
                Upload your first match
              </Button>
            </CardContent>
          </Card>
        )}

        <div className="flex flex-col gap-3">
          {matches?.map((match) => (
            <Link key={match.id} href={`/matches/${match.id}`}>
              <Card className="transition-colors hover:border-primary/50">
                <CardContent className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">{match.title}</p>
                    <div className="mt-1">
                      <ProcessingStatus stage={match.stage} errorMessage={match.error_message} />
                    </div>
                  </div>
                  <ArrowRight className="size-4 shrink-0 text-muted-foreground" />
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      </div>
    </DashboardShell>
  );
}
