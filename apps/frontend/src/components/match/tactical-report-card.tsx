"use client";

import { useState } from "react";
import type { TacticalReport } from "@scout-ai/shared";
import { Sparkles, Lightbulb, ClipboardList, Copy, Check } from "lucide-react";
import { Button } from "@/components/ui/button";

export function TacticalReportCard({ report }: { report: TacticalReport }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    const text = [
      report.summary,
      "",
      "Insights:",
      ...report.insights.map((i) => `- ${i}`),
      "",
      "Recommendations:",
      ...report.recommendations.map((r) => `- ${r}`),
    ].join("\n");
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  };

  return (
    <div className="rounded-xl border border-border bg-card p-4">
      <div className="mb-4 flex items-center justify-between">
        <p className="text-xs uppercase tracking-wider text-muted-foreground">
          AI Tactical Report
        </p>
        <Button variant="ghost" size="sm" onClick={handleCopy} className="h-7 gap-1.5 px-2 text-xs">
          {copied ? <Check className="size-3.5" /> : <Copy className="size-3.5" />}
          {copied ? "Copied" : "Copy"}
        </Button>
      </div>

      <div className="flex flex-col gap-5">
        <div>
          <div className="mb-1.5 flex items-center gap-1.5 text-sm font-medium">
            <Sparkles className="size-3.5 text-primary" />
            Summary
          </div>
          <p className="text-sm leading-relaxed text-muted-foreground">{report.summary}</p>
        </div>

        <div>
          <div className="mb-1.5 flex items-center gap-1.5 text-sm font-medium">
            <Lightbulb className="size-3.5 text-amber-400" />
            Insights
          </div>
          <ul className="flex flex-col gap-1.5">
            {report.insights.map((insight) => (
              <li key={insight} className="flex gap-2 text-sm text-muted-foreground">
                <span className="mt-1.5 size-1 shrink-0 rounded-full bg-amber-400" />
                {insight}
              </li>
            ))}
          </ul>
        </div>

        <div>
          <div className="mb-1.5 flex items-center gap-1.5 text-sm font-medium">
            <ClipboardList className="size-3.5 text-sky-400" />
            Recommendations
          </div>
          <ul className="flex flex-col gap-1.5">
            {report.recommendations.map((rec) => (
              <li key={rec} className="flex gap-2 text-sm text-muted-foreground">
                <span className="mt-1.5 size-1 shrink-0 rounded-full bg-sky-400" />
                {rec}
              </li>
            ))}
          </ul>
        </div>
      </div>

      <p className="mt-5 border-t border-border pt-3 font-mono text-[10px] text-muted-foreground">
        model: {report.model}
      </p>
    </div>
  );
}
