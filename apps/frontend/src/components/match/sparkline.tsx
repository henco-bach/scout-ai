const WIDTH = 100;
const HEIGHT = 28;
const PADDING = 2;

export function Sparkline({ values, color }: { values: number[]; color: string }) {
  if (values.length < 2) return null;

  const min = Math.min(...values);
  const max = Math.max(...values);
  const range = max - min || 1;
  const stepX = (WIDTH - PADDING * 2) / (values.length - 1);

  const path = values
    .map((v, i) => {
      const x = PADDING + i * stepX;
      const y = PADDING + (1 - (v - min) / range) * (HEIGHT - PADDING * 2);
      return `${i === 0 ? "M" : "L"}${x.toFixed(1)},${y.toFixed(1)}`;
    })
    .join(" ");

  return (
    <svg viewBox={`0 0 ${WIDTH} ${HEIGHT}`} className="mt-2 h-7 w-full">
      <path d={path} fill="none" stroke={color} strokeWidth={1.5} strokeLinecap="round" />
    </svg>
  );
}
