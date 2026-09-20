"use client";

import { useRouter } from "next/navigation";
import { useAppContext } from "@/context/AppContext";
import { Card } from "@/components/ui/Card";
import { RiskBadge } from "@/components/ui/Badge";
import { NetworkSvg } from "@/components/dashboard/NetworkSvg";
import { NetworkMap } from "@/components/dashboard/NetworkMap";
import { pct } from "@/lib/utils";

export default function NetworkPage() {
  const router = useRouter();
  const { stations } = useAppContext();

  return (
    <div className="animate-fade-in-up">
      <div className="mb-5">
        <h1 className="text-[24px] font-extrabold tracking-tight">Pipeline network</h1>
        <p className="mt-1 text-[13px] text-text-mute">
          {stations.length} pump stations from Mombasa (PS1) to Kisumu depot.
        </p>
      </div>

      <Card className="mb-4">
        <div className="mb-3 flex items-center justify-between"><div><h3 className="text-[14.5px] font-extrabold">Geographic view</h3><p className="mt-1 text-xs text-text-mute">Stations and the transport route plotted from configured coordinates.</p></div><span className="rounded-full bg-muted px-2.5 py-1 text-[11px] font-semibold text-text-mute">Interactive map</span></div>
        <NetworkMap />
      </Card>

      <Card className="mb-4">
        <h3 className="mb-3 text-[14.5px] font-extrabold">Schematic view</h3>
        <NetworkSvg width={900} height={130} />
      </Card>

      <Card padded={false}>
        <div className="p-5 pb-3">
          <h3 className="text-[14.5px] font-extrabold">Station detail</h3>
        </div>
        <div className="overflow-x-auto px-5 pb-5">
          <table className="w-full min-w-[640px] border-collapse text-[12.5px]">
            <thead>
              <tr>
                {["Station", "Location", "Distance", "Pumps", "Highest risk", "Status"].map((h) => (
                  <th
                    key={h}
                    className="border-b border-border px-1.5 py-2 text-left text-[11px] font-bold uppercase tracking-wide text-text-mute"
                  >
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {stations.map((s) => (
                <tr
                  key={s.code}
                  onClick={() => router.push(`/pumps?station=${s.code}`)}
                  className="cursor-pointer transition-colors hover:bg-bg"
                >
                  <td className="border-b border-black/[0.04] px-1.5 py-2.5 font-bold">{s.code}</td>
                  <td className="border-b border-black/[0.04] px-1.5 py-2.5">{s.name}</td>
                  <td className="border-b border-black/[0.04] px-1.5 py-2.5">{s.km_from_mombasa} km</td>
                  <td className="border-b border-black/[0.04] px-1.5 py-2.5">{s.pump_count}</td>
                  <td className="border-b border-black/[0.04] px-1.5 py-2.5">{pct(s.max_risk)}</td>
                  <td className="border-b border-black/[0.04] px-1.5 py-2.5">
                    <RiskBadge risk={s.max_risk} />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}
