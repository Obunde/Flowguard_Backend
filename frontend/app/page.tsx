"use client";

import Link from "next/link";
import { useAppContext } from "@/context/AppContext";
import { Card } from "@/components/ui/Card";
import { RiskBadge } from "@/components/ui/Badge";
import { NetworkSvg } from "@/components/dashboard/NetworkSvg";
import { days, pct, riskWord, sortByRiskDesc } from "@/lib/utils";

export default function DashboardPage() {
  const { openPump, stations, pumps, modelMetrics, atRiskPumps, criticalPumps, stationName } = useAppContext();
  const statTiles = [
    { icon: "⚠", iconBg: "bg-red-light", label: "Pumps at critical risk", value: criticalPumps.length, trend: "Requires action this week", trendClass: "text-red" },
    { icon: "◐", iconBg: "bg-amber-light", label: "Pumps on watch", value: atRiskPumps.length - criticalPumps.length, trend: "Monitor, no action yet", trendClass: "text-text-mute" },
    { icon: "✓", iconBg: "bg-green-light", label: "Healthy pumps", value: pumps.length - atRiskPumps.length, trend: "Operating normally", trendClass: "text-green" },
  ];
  const earliestFailure = atRiskPumps.filter((p) => p.rul_hours !== null);
  const earliestDays = earliestFailure.length
    ? days(Math.min(...earliestFailure.map((p) => p.rul_hours!)))
    : null;
  const highestRisk = sortByRiskDesc(pumps).slice(0, 6);
  const falseAlarmRate =
    modelMetrics.confusion_matrix[0][1] / (modelMetrics.confusion_matrix[0][0] + modelMetrics.confusion_matrix[0][1]);

  return (
    <div className="animate-fade-in-up">
      <div className="mb-5 flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-[24px] font-extrabold tracking-tight">Control room</h1>
          <p className="mt-1 text-[13px] text-text-mute">
            Fleet status across {stations.length} stations, {pumps.length} pumps — Mombasa to Kisumu.
          </p>
        </div>
        <div className="rounded-squircle-sm border border-border bg-surface px-3.5 py-2 text-[12.5px] font-semibold text-text-mute shadow-soft">
          Last model run: today 06:00 ▾
        </div>
      </div>

      <div className="mb-4 grid grid-cols-1 gap-3.5 sm:grid-cols-2 lg:grid-cols-4">
        {statTiles.map((tile) => (
          <Card key={tile.label} className="flex items-start gap-3">
            <div className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-squircle-sm text-[17px] ${tile.iconBg}`}>
              {tile.icon}
            </div>
            <div>
              <div className="text-[11.5px] font-semibold text-text-mute">{tile.label}</div>
              <div className="text-[23px] font-extrabold leading-tight">{tile.value}</div>
              <div className={`text-[11px] font-semibold ${tile.trendClass}`}>{tile.trend}</div>
            </div>
          </Card>
        ))}
        <Card className="flex items-start gap-3">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-squircle-sm bg-teal-light text-[17px]">
            ◈
          </div>
          <div>
            <div className="text-[11.5px] font-semibold text-text-mute">Earliest predicted failure</div>
            <div className="text-[23px] font-extrabold leading-tight">{earliestDays ? `${earliestDays}d` : "—"}</div>
            <div className="text-[11px] font-semibold text-text-mute">Lead time to act</div>
          </div>
        </Card>
      </div>

      <div className="mb-4 grid grid-cols-1 gap-4 lg:grid-cols-[1.5fr_1fr]">
        <Card>
          <div className="mb-3 flex items-center justify-between">
            <h3 className="text-[14.5px] font-extrabold">Pipeline network status</h3>
            <Link href="/network" className="text-[13px] font-semibold text-teal hover:underline">
              Open network view →
            </Link>
          </div>
          <NetworkSvg width={700} height={120} />
          <div className="mt-2 flex gap-4 text-[11px] text-text-mute">
            <span className="text-red">● Critical</span>
            <span className="text-amber">● Watch</span>
            <span className="text-green">● Healthy</span>
          </div>
        </Card>

        <Card>
          <div className="mb-3 flex items-center justify-between">
            <h3 className="text-[14.5px] font-extrabold">Priority actions</h3>
            <Link href="/alerts" className="text-[13px] font-semibold text-teal hover:underline">
              All alerts →
            </Link>
          </div>
          <div className="space-y-3.5">
            {atRiskPumps.slice(0, 4).map((p) => (
              <button
                key={p.pump_id}
                onClick={() => openPump(p.pump_id)}
                className="flex w-full items-start gap-3 text-left transition-opacity hover:opacity-70"
              >
                <div
                  className={`flex h-[34px] w-[34px] shrink-0 items-center justify-center rounded-squircle-sm text-[13px] ${
                    p.risk_probability > 0.5 ? "bg-red-light" : "bg-amber-light"
                  }`}
                >
                  ⚙
                </div>
                <div>
                  <div className="text-[12.5px] font-bold">
                    {p.pump_id} — {riskWord(p.risk_probability)}
                  </div>
                  <div className="text-[11px] text-text-mute">
                    {stationName(p.station_code)}
                    {p.rul_hours !== null ? ` · ${days(p.rul_hours)} days remaining` : ""}
                  </div>
                </div>
              </button>
            ))}
          </div>
        </Card>
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <Card padded={false}>
          <div className="flex items-center justify-between p-5 pb-3">
            <h3 className="text-[14.5px] font-extrabold">Highest-risk pumps</h3>
            <Link href="/pumps" className="text-[13px] font-semibold text-teal hover:underline">
              Full fleet →
            </Link>
          </div>
          <div className="overflow-x-auto px-5 pb-5">
            <table className="w-full border-collapse text-[12.5px]">
              <thead>
                <tr>
                  {["Pump", "Station", "Risk", "RUL", "Status"].map((h) => (
                    <th key={h} className="border-b border-border px-1.5 py-2 text-left text-[11px] font-bold uppercase tracking-wide text-text-mute">
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {highestRisk.map((p) => (
                  <tr
                    key={p.pump_id}
                    onClick={() => openPump(p.pump_id)}
                    className="cursor-pointer transition-colors hover:bg-bg"
                  >
                    <td className="border-b border-black/[0.04] px-1.5 py-2.5 font-bold">{p.pump_id}</td>
                    <td className="border-b border-black/[0.04] px-1.5 py-2.5">{stationName(p.station_code)}</td>
                    <td className="border-b border-black/[0.04] px-1.5 py-2.5">{pct(p.risk_probability)}</td>
                    <td className="border-b border-black/[0.04] px-1.5 py-2.5">
                      {p.rul_hours !== null ? `${days(p.rul_hours)}d` : "—"}
                    </td>
                    <td className="border-b border-black/[0.04] px-1.5 py-2.5">
                      <RiskBadge risk={p.risk_probability} />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>

        <Card>
          <div className="mb-3 flex items-center justify-between">
            <h3 className="text-[14.5px] font-extrabold">Model confidence</h3>
            <Link href="/model" className="text-[13px] font-semibold text-teal hover:underline">
              Full report →
            </Link>
          </div>
          {[
            ["Classification accuracy", pct(modelMetrics.classification_accuracy)],
            ["Failure-catch sensitivity", pct(modelMetrics.classification_sensitivity)],
            ["RUL mean absolute error", `${modelMetrics.rul_mae_hours} hours`],
            ["False alarm rate", pct(falseAlarmRate)],
          ].map(([k, v]) => (
            <div key={k} className="flex justify-between border-b border-black/[0.05] py-2 text-[12.5px] last:border-0">
              <span className="text-text-mute">{k}</span>
              <span className="font-bold">{v}</span>
            </div>
          ))}
          <div className="mt-3.5 rounded-squircle bg-teal-light p-3.5 text-[11.5px] text-[#0E6B63]">
            Flowgard&apos;s health deviation index is the strongest single predictor in the model — confirmed by SHAP
            across every flagged pump.
          </div>
        </Card>
      </div>
    </div>
  );
}
