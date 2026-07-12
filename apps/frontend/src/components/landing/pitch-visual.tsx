"use client";

import { motion } from "framer-motion";

const PITCH = { left: 20, right: 620, top: 20, bottom: 380 };
const MID_X = (PITCH.left + PITCH.right) / 2;
const MID_Y = (PITCH.top + PITCH.bottom) / 2;

const homePlayers = [
  { x: 40, y: 200 }, // GK
  { x: 100, y: 90 }, // DEF
  { x: 100, y: 150 },
  { x: 100, y: 250 },
  { x: 100, y: 310 },
  { x: 190, y: 120 }, // MID
  { x: 190, y: 200 },
  { x: 190, y: 280 },
  { x: 270, y: 100 }, // FWD
  { x: 270, y: 200 },
  { x: 270, y: 300 },
];

const awayPlayers = homePlayers.map((p) => ({ x: PITCH.right + PITCH.left - p.x, y: p.y }));

// A short home-team buildup: keeper to fullback, into midfield, out to the
// wing, and a cutback into the box, looping back to start.
const passSequence = [
  { x: 40, y: 200 },
  { x: 100, y: 250 },
  { x: 190, y: 280 },
  { x: 270, y: 300 },
  { x: 190, y: 200 },
  { x: 270, y: 100 },
  { x: 40, y: 200 },
];

function PenaltyArea({ side }: { side: "left" | "right" }) {
  const flip = side === "left";
  const boxX = flip ? PITCH.left : PITCH.right - 95;
  const sixX = flip ? PITCH.left : PITCH.right - 31;
  const spotX = flip ? PITCH.left + 63 : PITCH.right - 63;
  const arcStart = flip ? spotX + 50 * Math.cos((140 * Math.PI) / 180) : spotX - 50 * Math.cos((140 * Math.PI) / 180);

  return (
    <g stroke="var(--color-border)" strokeWidth="1.5" fill="none">
      {/* 18-yard box */}
      <rect x={boxX} y={MID_Y - 107} width={95} height={214} />
      {/* 6-yard box */}
      <rect x={sixX} y={MID_Y - 48.5} width={31} height={97} />
      {/* penalty spot */}
      <circle cx={spotX} cy={MID_Y} r="2.5" fill="var(--color-border)" />
      {/* penalty arc (only the part outside the box) */}
      <path
        d={
          flip
            ? `M ${spotX + 50 * Math.cos((-40 * Math.PI) / 180)} ${MID_Y + 50 * Math.sin((-40 * Math.PI) / 180)} A 50 50 0 0 1 ${spotX + 50 * Math.cos((40 * Math.PI) / 180)} ${MID_Y + 50 * Math.sin((40 * Math.PI) / 180)}`
            : `M ${spotX - 50 * Math.cos((-40 * Math.PI) / 180)} ${MID_Y + 50 * Math.sin((-40 * Math.PI) / 180)} A 50 50 0 0 0 ${spotX - 50 * Math.cos((40 * Math.PI) / 180)} ${MID_Y + 50 * Math.sin((40 * Math.PI) / 180)}`
        }
      />
      {/* goal */}
      <rect
        x={flip ? PITCH.left - 10 : PITCH.right}
        y={MID_Y - 19.4}
        width={10}
        height={38.8}
      />
    </g>
  );
}

export function PitchVisual() {
  return (
    <div className="relative mx-auto w-full max-w-3xl">
      <svg
        viewBox="0 0 640 400"
        className="w-full"
        role="img"
        aria-label="Illustration of tracked players in an 11 versus 11 formation on a regulation football pitch, with an animated passing sequence"
      >
        {/* outer touchlines / goal lines */}
        <rect
          x={PITCH.left}
          y={PITCH.top}
          width={PITCH.right - PITCH.left}
          height={PITCH.bottom - PITCH.top}
          rx="2"
          fill="none"
          stroke="var(--color-border)"
          strokeWidth="1.5"
        />
        {/* halfway line */}
        <line
          x1={MID_X}
          y1={PITCH.top}
          x2={MID_X}
          y2={PITCH.bottom}
          stroke="var(--color-border)"
          strokeWidth="1.5"
        />
        {/* center circle + spot */}
        <circle cx={MID_X} cy={MID_Y} r="50" fill="none" stroke="var(--color-border)" strokeWidth="1.5" />
        <circle cx={MID_X} cy={MID_Y} r="2.5" fill="var(--color-border)" />

        <PenaltyArea side="left" />
        <PenaltyArea side="right" />

        {/* corner arcs */}
        {[
          { cx: PITCH.left, cy: PITCH.top, sweep: 1 },
          { cx: PITCH.left, cy: PITCH.bottom, sweep: 0 },
          { cx: PITCH.right, cy: PITCH.top, sweep: 0 },
          { cx: PITCH.right, cy: PITCH.bottom, sweep: 1 },
        ].map((c, i) => (
          <path
            key={i}
            d={`M ${c.cx + (c.cx === PITCH.left ? 6 : -6)} ${c.cy} A 6 6 0 0 ${c.sweep} ${c.cx} ${c.cy + (c.cy === PITCH.top ? 6 : -6)}`}
            fill="none"
            stroke="var(--color-border)"
            strokeWidth="1.5"
          />
        ))}

        {/* passing route (subtle, static) */}
        <polyline
          points={passSequence.map((p) => `${p.x},${p.y}`).join(" ")}
          fill="none"
          stroke="var(--color-primary)"
          strokeWidth="1"
          strokeDasharray="4 4"
          opacity={0.35}
        />

        {homePlayers.map((p, i) => (
          <motion.circle
            key={`home-${i}`}
            cx={p.x}
            cy={p.y}
            r="5"
            fill="var(--color-primary)"
            initial={{ opacity: 0 }}
            animate={{ opacity: [0.6, 1, 0.6] }}
            transition={{ duration: 2.4, repeat: Infinity, delay: i * 0.12, ease: "easeInOut" }}
          />
        ))}
        {awayPlayers.map((p, i) => (
          <motion.circle
            key={`away-${i}`}
            cx={p.x}
            cy={p.y}
            r="5"
            fill="var(--color-rose-400, #fb7185)"
            initial={{ opacity: 0 }}
            animate={{ opacity: [0.6, 1, 0.6] }}
            transition={{ duration: 2.4, repeat: Infinity, delay: i * 0.12 + 0.3, ease: "easeInOut" }}
          />
        ))}

        {/* ball moving through the passing sequence */}
        <motion.circle
          r="4"
          fill="#ffd700"
          animate={{
            cx: passSequence.map((p) => p.x),
            cy: passSequence.map((p) => p.y),
          }}
          transition={{
            duration: 6,
            repeat: Infinity,
            ease: "easeInOut",
            times: passSequence.map((_, i) => i / (passSequence.length - 1)),
          }}
        />
      </svg>
    </div>
  );
}
