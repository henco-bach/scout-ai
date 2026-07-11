import { Reveal } from "@/components/landing/reveal";

const roadmap = [
  "Player scouting & similarity",
  "Expected goals & threat",
  "Sprint & fatigue detection",
  "Live match analysis",
  "AI scout & AI coach",
  "Women's football analytics",
];

export function Vision() {
  return (
    <section id="vision" className="border-t border-border px-6 py-24">
      <div className="mx-auto max-w-3xl text-center">
        <Reveal>
          <p className="font-heading text-2xl leading-snug tracking-tight sm:text-3xl">
            &ldquo;Professional football analysis should not only exist for
            billion-dollar clubs.&rdquo;
          </p>
        </Reveal>

        <Reveal delay={0.1} className="mt-12">
          <h2 className="font-heading text-sm font-medium uppercase tracking-wider text-muted-foreground">
            On the roadmap
          </h2>
          <div className="mt-5 flex flex-wrap justify-center gap-2">
            {roadmap.map((item) => (
              <span
                key={item}
                className="rounded-full border border-border px-3 py-1.5 text-xs text-muted-foreground"
              >
                {item}
              </span>
            ))}
          </div>
        </Reveal>
      </div>
    </section>
  );
}
