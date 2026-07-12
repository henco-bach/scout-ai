import { Reveal } from "@/components/landing/reveal";

export function Mission() {
  return (
    <section id="mission" className="border-t border-border px-6 py-24">
      <div className="mx-auto grid max-w-5xl gap-12 md:grid-cols-2">
        <Reveal>
          <h2 className="font-heading text-sm font-medium uppercase tracking-wider text-muted-foreground">
            The Problem
          </h2>
          <p className="mt-4 text-2xl leading-snug tracking-tight">
            Professional football analytics software costs thousands of
            dollars a month and needs a dedicated analyst to run it. Most
            clubs simply cannot afford it, so millions of talented
            footballers are never discovered.
          </p>
        </Reveal>

        <Reveal delay={0.1}>
          <h2 className="font-heading text-sm font-medium uppercase tracking-wider text-muted-foreground">
            Our Mission
          </h2>
          <p className="mt-4 text-2xl leading-snug tracking-tight">
            Every school. Every academy. Every township club. Every amateur
            and women&apos;s team. Every coach. Should have access to
            professional football intelligence, using only a smartphone
            recording.
          </p>
        </Reveal>
      </div>
    </section>
  );
}
