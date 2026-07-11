import { Loader2, CheckCircle2, XCircle } from "lucide-react";
import type { ProcessingStage } from "@scout-ai/shared";

const stageLabels: Record<ProcessingStage, string> = {
  uploaded: "Queued for analysis...",
  analyzing_video: "Detecting and tracking players...",
  generating_report: "Generating tactical report...",
  completed: "Analysis complete",
  failed: "Analysis failed",
};

export function ProcessingStatus({
  stage,
  errorMessage,
}: {
  stage: ProcessingStage;
  errorMessage: string | null;
}) {
  if (stage === "completed") {
    return (
      <div className="flex items-center gap-2 text-sm text-primary">
        <CheckCircle2 className="size-4" />
        {stageLabels.completed}
      </div>
    );
  }

  if (stage === "failed") {
    return (
      <div className="flex items-center gap-2 text-sm text-destructive">
        <XCircle className="size-4" />
        {errorMessage ?? stageLabels.failed}
      </div>
    );
  }

  return (
    <div className="flex items-center gap-2 text-sm text-muted-foreground">
      <Loader2 className="size-4 animate-spin text-primary" />
      {stageLabels[stage]}
    </div>
  );
}
