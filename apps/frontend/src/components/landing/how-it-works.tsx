import { Upload, ScanEye, LineChart, FileCheck } from "lucide-react";
import { Reveal } from "@/components/landing/reveal";

const steps = [
  {
    icon: Upload,
    title: "Upload Match",
    description: "One smartphone recording of the full match. That's it.",
  },
  {
    icon: ScanEye,
    title: "AI Watches Football",
    description:
      "Players are detected and tracked across every frame — position, movement, team.",
  },
  {
    icon: LineChart,
    title: "Statistics Are Computed",
    description:
      "Heatmaps, possession, passing networks, and average positions, generated from tracking data.",
  },
  {
    icon: FileCheck,
    title: "Tactical Report Delivered",
    description:
      "An AI coach report explains what happened and what to work on next.",
  },
];

export function HowItWorks() {
  return (
    <section id="how-it-works" className="border-t border-border px-6 py-24">
      <div className="mx-auto max-w-5xl">
        <Reveal className="mx-auto max-w-xl text-center">
          <h2 className="font-heading text-3xl font-semibold tracking-tight sm:text-4xl">
            How It Works
          </h2>
        </Reveal>

        <div className="relative mt-16 grid gap-10 sm:grid-cols-2 lg:grid-cols-4">
          <div
            className="absolute top-6 right-0 left-0 hidden h-px bg-border lg:block"
            aria-hidden
          />
          {steps.map((step, i) => (
            <Reveal key={step.title} delay={i * 0.08} className="relative">
              <div className="flex size-12 items-center justify-center rounded-full border border-border bg-background">
                <step.icon className="size-5 text-primary" strokeWidth={1.75} />
              </div>
              <h3 className="mt-4 font-medium">
                <span className="mr-2 font-mono text-xs text-muted-foreground">
                  {String(i + 1).padStart(2, "0")}
                </span>
                {step.title}
              </h3>
              <p className="mt-1.5 text-sm text-muted-foreground">
                {step.description}
              </p>
            </Reveal>
          ))}
        </div>
      </div>
    </section>
  );
}
