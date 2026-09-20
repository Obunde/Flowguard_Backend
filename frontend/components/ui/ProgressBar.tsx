export function ProgressBar({ percent, color }: { percent: number; color: string }) {
  const clamped = Math.max(0, Math.min(100, percent));
  return (
    <div className="h-[7px] w-full overflow-hidden rounded-pill bg-black/[0.06]">
      <div
        className="h-full rounded-pill transition-[width] duration-500 ease-out"
        style={{ width: `${clamped}%`, background: color }}
      />
    </div>
  );
}
