"use client";

import { useAppContext } from "@/context/AppContext";
import { Card } from "@/components/ui/Card";
import { RiskBadge } from "@/components/ui/Badge";
import { ProgressBar } from "@/components/ui/ProgressBar";
import { riskColorVar } from "@/lib/utils";

export default function FlowgardPage() {
  const { openPump, pumps, atRiskPumps, healthyPumps, stationName } = useAppContext();
  const avgHealthy = healthyPumps.reduce((s, p) => s + p.health_deviation_index, 0) / healthyPumps.length;
  const avgRisk = atRiskPumps.reduce((s, p) => s + p.health_deviation_index, 0) / atRiskPumps.length;
  const ranked = [...pumps].sort((a, b) => b.health_deviation_index - a.health_deviation_index).slice(0, 14);

  return (
    <div className="animate-fade-in-up">
      <div className="mb-5">
        <h1 className="text-[24px] font-extrabold tracking-tight">Flowgard reconciliation engine</h1>
        <p className="mt-1 text-[13px] text-text-mute">
          Physics-referenced pressure residual — the project&apos;s core differentiator.
        </p>
      </div>

      <div className="glass-dark mb-4 rounded-squircle-lg p-5 text-[#dce6f2] shadow-elevated">
        <div className="text-[13px] leading-[1.75]">
          <b className="text-white">How it works.</b> For every pump, Flowgard simulates the discharge pressure that{" "}
          <i>should</i> be observed given the motor current, using a hydraulic reference fitted on that pump&apos;s own
          healthy baseline. The gap between actual and simulated pressure is the residual:
          <div className="my-3 rounded-squircle bg-white/[0.08] px-4 py-3 font-mono text-[12.5px] text-[#8FE3D6]">
            Pressure residual = Actual pressure − Simulated pressure
            <br />
            Health deviation index = rolling mean |residual| ÷ calibration constant
          </div>
          This gives the classifier a <b className="text-white">physics anomaly</b> alongside its purely statistical
          rolling-window features — two structurally different views of the same degradation.
        </div>
      </div>

      <div className="mb-4 grid grid-cols-1 gap-3.5 sm:grid-cols-3">
        <Card className="flex items-start gap-3">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-squircle-sm bg-green-light text-[17px]">
            ✓
          </div>
          <div>
            <div className="text-[11.5px] font-semibold text-text-mute">Mean HDI — healthy pumps</div>
            <div className="text-[23px] font-extrabold leading-tight">{avgHealthy.toFixed(3)}</div>
            <div className="text-[11px] font-semibold text-green">Baseline</div>
          </div>
        </Card>
        <Card className="flex items-start gap-3">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-squircle-sm bg-red-light text-[17px]">
            ⚠
          </div>
          <div>
            <div className="text-[11.5px] font-semibold text-text-mute">Mean HDI — flagged pumps</div>
            <div className="text-[23px] font-extrabold leading-tight">{avgRisk.toFixed(3)}</div>
            <div className="text-[11px] font-semibold text-red">{(avgRisk / avgHealthy).toFixed(1)}× baseline</div>
          </div>
        </Card>
        <Card className="flex items-start gap-3">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-squircle-sm bg-teal-light text-[17px]">
            ◈
          </div>
          <div>
            <div className="text-[11.5px] font-semibold text-text-mute">SHAP rank in model</div>
            <div className="text-[23px] font-extrabold leading-tight">#1</div>
            <div className="text-[11px] font-semibold text-green">Strongest single predictor</div>
          </div>
        </Card>
      </div>

      <Card padded={false}>
        <div className="p-5 pb-3">
          <h3 className="text-[14.5px] font-extrabold">Health deviation index — all pumps</h3>
        </div>
        <div className="overflow-x-auto px-5 pb-5">
          <table className="w-full min-w-[620px] border-collapse text-[12.5px]">
            <thead>
              <tr>
                {["Pump", "Station", "HDI", "Deviation vs baseline", "Status"].map((h) => (
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
              {ranked.map((p) => (
                <tr
                  key={p.pump_id}
                  onClick={() => openPump(p.pump_id)}
                  className="cursor-pointer transition-colors hover:bg-bg"
                >
                  <td className="border-b border-black/[0.04] px-1.5 py-2.5 font-bold">{p.pump_id}</td>
                  <td className="border-b border-black/[0.04] px-1.5 py-2.5">{stationName(p.station_code)}</td>
                  <td className="border-b border-black/[0.04] px-1.5 py-2.5">{p.health_deviation_index.toFixed(3)}</td>
                  <td className="w-48 border-b border-black/[0.04] px-1.5 py-2.5">
                    <ProgressBar
                      percent={Math.min((p.health_deviation_index / 0.7) * 100, 100)}
                      color={riskColorVar(p.risk_probability)}
                    />
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
    </div>
  );
}
