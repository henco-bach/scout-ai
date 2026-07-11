"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { PitchVisual } from "@/components/landing/pitch-visual";

export function Hero() {
  return (
    <section className="relative overflow-hidden px-6 pb-20 pt-24 sm:pt-32">
      <div
        className="pointer-events-none absolute inset-x-0 top-0 -z-10 h-[480px] opacity-[0.15]"
        style={{
          background:
            "radial-gradient(ellipse 60% 50% at 50% 0%, var(--color-primary), transparent)",
        }}
      />

      <div className="mx-auto flex max-w-4xl flex-col items-center text-center">
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="mb-6 rounded-full border border-border px-4 py-1.5 text-xs text-muted-foreground"
        >
          Built in South Africa. Built for the world.
        </motion.div>

        <motion.h1
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
          className="font-heading text-5xl font-semibold tracking-tight sm:text-6xl md:text-7xl"
        >
          Football Intelligence
          <br />
          for Every Team.
        </motion.h1>

        <motion.p
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="mt-6 max-w-xl text-lg text-muted-foreground"
        >
          Professional AI-powered football analysis from a single smartphone
          video. Player tracking, heatmaps, and tactical reports — built for
          every club, not just the billion-dollar ones.
        </motion.p>

        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.3 }}
          className="mt-10 flex flex-col gap-3 sm:flex-row"
        >
          <Button size="lg" nativeButton={false} render={<Link href="/upload" />}>
            Upload Match
          </Button>
          <Button
            size="lg"
            variant="outline"
            nativeButton={false}
            render={<Link href="/matches" />}
          >
            View Demo
          </Button>
        </motion.div>
      </div>

      <motion.div
        initial={{ opacity: 0, y: 24 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.4 }}
        className="mx-auto mt-20 max-w-4xl"
      >
        <div className="rounded-2xl border border-border bg-card p-8">
          <PitchVisual />
        </div>
      </motion.div>
    </section>
  );
}
