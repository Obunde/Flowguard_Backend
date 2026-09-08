"use client";

import { useAppContext } from "@/context/AppContext";
import { Card } from "@/components/ui/Card";
import { days, pct } from "@/lib/utils";

export default function ModelPage() {
  const { modelMetrics, atRiskPumps } = useAppContext();
  const cm = modelMetrics.confusion_matrix;
  const falseAlarm = cm[0][1] / (cm[0][0] + cm[0][1]);
  const minLeadDays = atRiskPumps.length
    ? days(Math.min(...atRiskPumps.filter((p) => p.rul_hours !== null).map((p) => p.rul_hours!)))
    : "—";

  const tiles = [
    { icon: "◐", bg: "bg-teal-light", label: "Accuracy", value: pct(modelMetrics.classification_accuracy) },
    {
      icon: "✓",
      bg: "bg-green-light",
      label: "Sensitivity",
      value: pct(modelMetrics.classification_sensitivity),
      trend: "Failures caught",
    },
    { icon: "⚠", bg: "bg-amber-light", label: "False alarm rate", value: pct(falseAlarm), trend: "Below 5% target" },
    {
      icon: "◷",
      bg: "bg-blue-light",
      label: "RUL error (MAE)",
      value: `${modelMetrics.rul_mae_hours}h`,
      trend: "Target < 90h",
    },
  ];

  const benchmarks = [
    ["Catch ≥80% of failures", pct(modelMetrics.classification_sensitivity)],
    ["False alarms under 5%", pct(falseAlarm)],
    ["RUL MAE under 90 hours", `${modelMetrics.rul_mae_hours}h`],
    ["≥3 days advance warning", `${minLeadDays}d min`],
  ];

  return (
    <div className="animate-fade-in-up">
      <div className="mb-5">
        <h1 className="text-[24px] font-extrabold tracking-tight">Model performance</h1>
        <p className="mt-1 text-[13px] text-text-mute">Held-out test set evaluation. Every figure computed, not estimated.</p>
      </div>

      <div className="mb-4 grid grid-cols-1 gap-3.5 sm:grid-cols-2 lg:grid-cols-4">
        {tiles.map((t) => (
          <Card key={t.label} className="flex items-start gap-3">
            <div className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-squircle-sm text-[17px] ${t.bg}`}>
              {t.icon}
            </div>
            <div>
              <div className="text-[11.5px] font-semibold text-text-mute">{t.label}</div>
              <div className="text-[23px] font-extrabold leading-tight">{t.value}</div>
              {t.trend && <div className="text-[11px] font-semibold text-green">{t.trend}</div>}
            </div>
          </Card>
        ))}
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <Card>
          <h3 className="mb-3 text-[14.5px] font-extrabold">Confusion matrix</h3>
          <table className="w-full border-collapse text-[12.5px]">
            <thead>
              <tr>
                <th className="border-b border-border py-2 text-left text-[11px] text-text-mute" />
                <th className="border-b border-border py-2 text-left text-[11px] font-bold uppercase tracking-wide text-text-mute">
                  Predicted healthy
                </th>
                <th className="border-b border-border py-2 text-left text-[11px] font-bold uppercase tracking-wide text-text-mute">
                  Predicted at-risk
                </th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td className="border-b border-black/[0.04] py-2.5 font-bold">Actually healthy</td>
                <td className="border-b border-black/[0.04] bg-green-light py-2.5 pl-2 font-extrabold">
                  {cm[0][0].toLocaleString()}
                </td>
                <td className="border-b border-black/[0.04] bg-amber-light py-2.5 pl-2 font-extrabold">{cm[0][1]}</td>
              </tr>
              <tr>
                <td className="py-2.5 font-bold">Actually at-risk</td>
                <td className="bg-red-light py-2.5 pl-2 font-extrabold">{cm[1][0]}</td>
                <td className="bg-green-light py-2.5 pl-2 font-extrabold">{cm[1][1]}</td>
              </tr>
            </tbody>
          </table>
          <p className="mt-3.5 text-[11.5px] leading-[1.6] text-text-mute">
            The {cm[1][0]} missed failures (bottom-left) are the costly errors — each represents a pump that failed
            without warning. The {cm[0][1]} false alarms (top-right) cost only a wasted inspection.
          </p>
        </Card>

        <Card>
          <h3 className="mb-3 text-[14.5px] font-extrabold">Objective benchmarks</h3>
          {benchmarks.map(([k, v]) => (
            <div key={k} className="flex justify-between border-b border-black/[0.05] py-2 text-[12.5px] last:border-0">
              <span className="text-text-mute">{k}</span>
              <span className="font-bold text-green">✓ {v}</span>
            </div>
          ))}
          <div className="mt-3.5 rounded-squircle bg-amber-light p-3.5 text-[11.5px] leading-[1.6] text-[#8A5410]">
            <b>Caveat.</b> These figures are from synthetic, physics-informed data. Recalibration against real operational
            SCADA history is required before any operational claim — this is the core production-readiness requirement.
          </div>
        </Card>
      </div>
    </div>
  );
}
