"use client";

import { motion } from "framer-motion";

const homePlayers = [
  { x: 80, y: 120 },
  { x: 140, y: 60 },
  { x: 140, y: 180 },
  { x: 220, y: 100 },
  { x: 220, y: 160 },
];

const awayPlayers = [
  { x: 560, y: 120 },
  { x: 500, y: 60 },
  { x: 500, y: 180 },
  { x: 420, y: 100 },
  { x: 420, y: 160 },
];

export function PitchVisual() {
  return (
    <div className="relative mx-auto w-full max-w-3xl">
      <svg
        viewBox="0 0 640 240"
        className="w-full"
        role="img"
        aria-label="Abstract illustration of tracked players on a football pitch"
      >
        <rect
          x="4"
          y="4"
          width="632"
          height="232"
          rx="12"
          fill="none"
          stroke="var(--color-border)"
          strokeWidth="1"
        />
        <line x1="320" y1="4" x2="320" y2="236" stroke="var(--color-border)" strokeWidth="1" />
        <circle cx="320" cy="120" r="40" fill="none" stroke="var(--color-border)" strokeWidth="1" />

        {homePlayers.map((p, i) => (
          <motion.circle
            key={`home-${i}`}
            cx={p.x}
            cy={p.y}
            r="5"
            fill="var(--color-primary)"
            initial={{ opacity: 0 }}
            animate={{ opacity: [0.6, 1, 0.6] }}
            transition={{ duration: 2.4, repeat: Infinity, delay: i * 0.2, ease: "easeInOut" }}
          />
        ))}
        {awayPlayers.map((p, i) => (
          <motion.circle
            key={`away-${i}`}
            cx={p.x}
            cy={p.y}
            r="5"
            fill="var(--color-muted-foreground)"
            initial={{ opacity: 0 }}
            animate={{ opacity: [0.6, 1, 0.6] }}
            transition={{ duration: 2.4, repeat: Infinity, delay: i * 0.2 + 0.3, ease: "easeInOut" }}
          />
        ))}

        <motion.path
          d={`M ${homePlayers[3].x} ${homePlayers[3].y} L ${homePlayers[4].x} ${homePlayers[4].y}`}
          stroke="var(--color-primary)"
          strokeWidth="1"
          strokeDasharray="4 4"
          initial={{ pathLength: 0, opacity: 0 }}
          animate={{ pathLength: 1, opacity: 0.6 }}
          transition={{ duration: 1.2, delay: 0.6 }}
        />
      </svg>
    </div>
  );
}
