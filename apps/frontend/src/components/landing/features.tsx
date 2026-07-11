import {
  Users,
  Route,
  Flame,
  PieChart,
  Share2,
  FileText,
} from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Reveal } from "@/components/landing/reveal";

const features = [
  {
    icon: Users,
    title: "Player Detection & Tracking",
    description:
      "Every player identified and followed across the full match, frame by frame.",
  },
  {
    icon: Flame,
    title: "Heatmaps",
    description:
      "See exactly where each player spent their time on the pitch.",
  },
  {
    icon: PieChart,
    title: "Possession & Accuracy",
    description:
      "Team possession share and pass accuracy, computed directly from tracked movement.",
  },
  {
    icon: Share2,
    title: "Passing Networks",
    description:
      "Visualize how the ball moved between players and where attacks broke down.",
  },
  {
    icon: Route,
    title: "Average Positions",
    description:
      "Understand shape and spacing with each player's average position on the pitch.",
  },
  {
    icon: FileText,
    title: "AI Tactical Reports",
    description:
      "A professional analyst-style report with coach recommendations — generated from your match, not invented.",
  },
];

export function Features() {
  return (
    <section id="features" className="border-t border-border px-6 py-24">
      <div className="mx-auto max-w-5xl">
        <Reveal className="mx-auto max-w-xl text-center">
          <h2 className="font-heading text-3xl font-semibold tracking-tight sm:text-4xl">
            Everything a match analyst gives you
          </h2>
          <p className="mt-4 text-muted-foreground">
            One upload produces the full breakdown — no manual tagging, no
            analyst on payroll.
          </p>
        </Reveal>

        <div className="mt-16 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {features.map((feature, i) => (
            <Reveal key={feature.title} delay={i * 0.05}>
              <Card className="h-full">
                <CardContent className="flex flex-col gap-4">
                  <feature.icon
                    className="size-5 text-primary"
                    strokeWidth={1.75}
                  />
                  <div>
                    <h3 className="font-medium">{feature.title}</h3>
                    <p className="mt-1.5 text-sm text-muted-foreground">
                      {feature.description}
                    </p>
                  </div>
                </CardContent>
              </Card>
            </Reveal>
          ))}
        </div>
      </div>
    </section>
  );
}
