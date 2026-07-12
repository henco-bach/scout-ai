"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useMutation } from "@tanstack/react-query";
import { Loader2, ArrowRight } from "lucide-react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { DashboardShell } from "@/components/dashboard/dashboard-shell";
import { VideoDropzone } from "@/components/upload/video-dropzone";
import { uploadMatch } from "@/lib/api/matches";

function parseKickoffTime(value: string): number {
  if (!value.trim()) return 0;
  const parts = value.trim().split(":").map(Number);
  if (parts.length === 0 || parts.some(Number.isNaN)) return 0;
  return parts.reduce((total, part) => total * 60 + part, 0);
}

export default function UploadPage() {
  const router = useRouter();
  const [title, setTitle] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [kickoffTime, setKickoffTime] = useState("");

  const mutation = useMutation({
    mutationFn: () => uploadMatch(title || file!.name, file!, parseKickoffTime(kickoffTime)),
    onSuccess: (match) => {
      router.push(`/matches/${match.id}`);
    },
    onError: () => {
      toast.error("Upload failed. Check the backend is running and try again.");
    },
  });

  return (
    <DashboardShell>
      <div className="mx-auto w-full max-w-xl px-6 py-16">
        <h1 className="font-heading text-3xl font-semibold tracking-tight">Upload Match</h1>
        <p className="mt-2 text-muted-foreground">
          One video, analyzed automatically: player tracking, heatmaps, and a tactical
          report.
        </p>

        <form
          className="mt-10 flex flex-col gap-6"
          onSubmit={(e) => {
            e.preventDefault();
            if (!file) return;
            mutation.mutate();
          }}
        >
          <div className="flex flex-col gap-2">
            <Label htmlFor="title">Match title</Label>
            <Input
              id="title"
              placeholder="U15s vs Riverside FC"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              disabled={mutation.isPending}
            />
          </div>

          <div className="flex flex-col gap-2">
            <Label>Match video</Label>
            <VideoDropzone file={file} onFileChange={setFile} />
          </div>

          <div className="flex flex-col gap-2">
            <Label htmlFor="kickoff">Kickoff time (optional)</Label>
            <Input
              id="kickoff"
              placeholder="mm:ss, e.g. 1:45"
              value={kickoffTime}
              onChange={(e) => setKickoffTime(e.target.value)}
              disabled={mutation.isPending}
            />
            <p className="text-xs text-muted-foreground">
              If the video opens with intros, warmups, or a lineup, tell us when the ball
              actually kicks off so analysis covers real play instead.
            </p>
          </div>

          <Button
            type="submit"
            size="lg"
            disabled={!file || mutation.isPending}
            className="w-full"
          >
            {mutation.isPending ? (
              <>
                <Loader2 className="size-4 animate-spin" />
                Uploading...
              </>
            ) : (
              <>
                Analyze Match
                <ArrowRight className="size-4" />
              </>
            )}
          </Button>
        </form>
      </div>
    </DashboardShell>
  );
}
