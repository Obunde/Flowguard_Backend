import type { ShapFeature } from "@/data/types";

export function ShapTrack({ features }: { features: ShapFeature[] }) {
  const maxAbs = Math.max(...features.map((f) => Math.abs(f.value)));

  return (
    <div className="space-y-2">
      {features.map((f) => {
        const width = (Math.abs(f.value) / maxAbs) * 100;
        const positive = f.value > 0;
        return (
          <div key={f.feature} className="flex items-center gap-3 text-[11.5px]">
            <div className="w-36 shrink-0 text-right text-text-mute">{f.feature.replace(/_/g, " ")}</div>
            <div className="h-3.5 flex-1 overflow-hidden rounded-md bg-black/[0.05]">
              <div
                className="h-full rounded-md transition-[width] duration-500 ease-out"
                style={{
                  width: `${width}%`,
                  background: positive ? "var(--color-red)" : "var(--color-teal)",
                }}
              />
            </div>
            <div className="w-14 text-[10.5px] text-text-mute">
              {positive ? "+" : ""}
              {f.value.toFixed(3)}
            </div>
          </div>
        );
      })}
    </div>
  );
}
