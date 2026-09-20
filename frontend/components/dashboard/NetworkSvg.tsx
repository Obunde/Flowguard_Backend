"use client";

import { useRouter } from "next/navigation";
import { useAppContext } from "@/context/AppContext";
import { riskColorVar } from "@/lib/utils";

export function NetworkSvg({ width = 700, height = 120 }: { width?: number; height?: number }) {
  const router = useRouter();
  const { stations } = useAppContext();
  const maxKm = Math.max(...stations.map((s) => s.km_from_mombasa));
  const pad = 34;
  const span = width - pad * 2;
  const y = height / 2 + 5;

  let x = stations.map((s, index) =>
    maxKm > 0
      ? pad + (s.km_from_mombasa / maxKm) * span
      : pad + (index / Math.max(stations.length - 1, 1)) * span,
  );
  for (let i = 1; i < x.length; i++) {
    if (x[i] - x[i - 1] < 46) x[i] = x[i - 1] + 46;
  }
  const overflow = x[x.length - 1] - (width - pad);
  if (overflow > 0) {
    const k = (width - pad - x[0]) / (x[x.length - 1] - x[0]);
    x = x.map((v) => x[0] + (v - x[0]) * k);
  }

  return (
    <svg viewBox={`0 0 ${width} ${height}`} width="100%" height={height} role="img" aria-label="Pipeline network status">
      <line x1={pad} y1={y} x2={width - pad} y2={y} stroke="#C9D3E0" strokeWidth={2.5} />
      {stations.map((s, i) => {
        const color = riskColorVar(s.max_risk);
        const r = s.alert ? 8 : 6;
        const shortName = s.name.length > 8 ? s.name.slice(0, 7) + "…" : s.name;
        return (
          <g
            key={s.code}
            className="cursor-pointer"
            onClick={() => router.push("/network")}
          >
            <circle cx={x[i]} cy={y} r={r} fill={color} stroke="#fff" strokeWidth={2} />
            <text x={x[i]} y={y - 15} textAnchor="middle" fontSize={9} fontWeight={700} fill="#1B2436">
              {s.code}
            </text>
            <text x={x[i]} y={y + 22} textAnchor="middle" fontSize={8} fill="#6B7690">
              {shortName}
            </text>
          </g>
        );
      })}
    </svg>
  );
}
