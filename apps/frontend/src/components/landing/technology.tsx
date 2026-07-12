import { Reveal } from "@/components/landing/reveal";

const stack = [
  {
    title: "Computer Vision",
    items: ["OpenCV", "Ultralytics YOLO", "ByteTrack", "Roboflow"],
  },
  {
    title: "AI Analysis",
    items: ["Fireworks AI", "AMD Developer Cloud (ROCm GPU)"],
  },
  {
    title: "Core Stack",
    items: ["FastAPI", "Next.js", "SQLite", "Docker"],
  },
];

export function Technology() {
  return (
    <section id="technology" className="border-t border-border px-6 py-24">
      <div className="mx-auto max-w-5xl">
        <Reveal className="mx-auto max-w-xl text-center">
          <h2 className="font-heading text-3xl font-semibold tracking-tight sm:text-4xl">
            Real computer vision. Real AI.
          </h2>
          <p className="mt-4 text-muted-foreground">
            Every stage of the pipeline is modular. Detection, tracking, and
            report generation can each be swapped as better models arrive.
          </p>
        </Reveal>

        <div className="mt-16 grid gap-8 sm:grid-cols-3">
          {stack.map((group, i) => (
            <Reveal key={group.title} delay={i * 0.08}>
              <h3 className="font-mono text-xs uppercase tracking-wider text-muted-foreground">
                {group.title}
              </h3>
              <ul className="mt-3 space-y-2">
                {group.items.map((item) => (
                  <li key={item} className="text-sm">
                    {item}
                  </li>
                ))}
              </ul>
            </Reveal>
          ))}
        </div>
      </div>
    </section>
  );
}
