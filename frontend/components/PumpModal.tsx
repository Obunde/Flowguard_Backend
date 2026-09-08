"use client";

import { useRouter } from "next/navigation";
import { useAppContext } from "@/context/AppContext";
import { Modal } from "@/components/ui/Modal";
import { RiskBadge } from "@/components/ui/Badge";
import { ShapTrack } from "@/components/ui/ShapTrack";
import { Button } from "@/components/ui/Button";
import { pct, riskColorVar } from "@/lib/utils";

const COMPONENT_LABELS: Record<string, string> = {
  bearing: "Bearing",
  impeller: "Impeller",
  seal: "Seal",
};

function componentColor(v: number) {
  return v > 0.4 ? "var(--color-red)" : v > 0.25 ? "var(--color-amber)" : "var(--color-green)";
}

export function PumpModal() {
  const { openPumpId, closeModal, showToast, pumps, stationName, refreshData, can } = useAppContext();
  const router = useRouter();
  const pump = pumps.find((p) => p.pump_id === openPumpId) ?? null;

  async function raiseWorkOrder() {
    if (!pump?.id) {
      showToast("This pump is missing its backend identifier");
      return;
    }
    const response = await fetch(`/api/backend/api/v1/work-orders/auto-generate/pumps/${pump.id}`, {
      method: "POST",
    });
    if (!response.ok) {
      const result = (await response.json().catch(() => null)) as { detail?: string } | null;
      showToast(result?.detail ?? `Unable to raise a work order for ${pump.pump_id}`);
      return;
    }
    await refreshData();
    closeModal();
    showToast(`Work order raised for ${pump.pump_id}`);
    router.push("/workorders");
  }

  return (
    <Modal open={!!pump} onClose={closeModal}>
      {pump && (
        <>
          <div className="mb-1 flex items-start justify-between gap-3">
            <h3 className="flex items-center gap-2 text-[19px] font-extrabold">
              {pump.pump_id}
              <RiskBadge risk={pump.risk_probability} />
            </h3>
            <button
              onClick={closeModal}
              aria-label="Close"
              className="rounded-full p-1 text-[18px] leading-none text-text-mute transition-colors hover:bg-black/[0.05] hover:text-text"
            >
              ×
            </button>
          </div>
          <div className="mb-5 text-[12.5px] text-text-mute">
            {pump.station_code} — {stationName(pump.station_code)}
          </div>

          <div className="mb-5 grid grid-cols-3 gap-3">
            <div className="rounded-squircle bg-bg p-4">
              <div className="text-[11.5px] font-semibold text-text-mute">7-day failure risk</div>
              <div className="text-[22px] font-extrabold" style={{ color: riskColorVar(pump.risk_probability) }}>
                {pct(pump.risk_probability)}
              </div>
            </div>
            <div className="rounded-squircle bg-bg p-4">
              <div className="text-[11.5px] font-semibold text-text-mute">Remaining useful life</div>
              <div className="text-[22px] font-extrabold">{pump.rul_hours !== null ? `${pump.rul_hours}h` : "—"}</div>
              <div className="text-[10.5px] text-text-mute">
                {pump.rul_hours !== null ? `90% CI ${pump.rul_ci_low}–${pump.rul_ci_high}h` : "Healthy"}
              </div>
            </div>
            <div className="rounded-squircle bg-bg p-4">
              <div className="text-[11.5px] font-semibold text-text-mute">Flowgard HDI</div>
              <div
                className="text-[22px] font-extrabold"
                style={{
                  color:
                    pump.health_deviation_index > 0.4
                      ? "var(--color-red)"
                      : pump.health_deviation_index > 0.2
                        ? "var(--color-amber)"
                        : "var(--color-green)",
                }}
              >
                {pump.health_deviation_index.toFixed(2)}
              </div>
            </div>
          </div>

          <h4 className="mb-2.5 text-[14px] font-extrabold">Live sensor readings</h4>
          <dl className="mb-5">
            {[
              ["Vibration", `${pump.sensors.vibration_g} g`],
              ["Temperature", `${pump.sensors.temperature_c} °C`],
              ["Discharge pressure", `${pump.sensors.pressure_bar} bar`],
              ["Motor current", `${pump.sensors.motor_current_a} A`],
            ].map(([k, v]) => (
              <div key={k} className="flex justify-between border-b border-black/[0.05] py-2 text-[12.5px] last:border-0">
                <dt className="text-text-mute">{k}</dt>
                <dd className="font-bold">{v}</dd>
              </div>
            ))}
          </dl>

          <h4 className="mb-2.5 text-[14px] font-extrabold">Why this pump was flagged (SHAP)</h4>
          <div className="mb-5">
            <ShapTrack features={pump.shap_top_features} />
          </div>

          <h4 className="mb-2.5 text-[14px] font-extrabold">Component attribution</h4>
          <div className="mb-6 flex gap-2.5">
            {(Object.entries(pump.component_states) as [keyof typeof COMPONENT_LABELS, number][]).map(([key, value]) => (
              <div key={key} className="flex-1 rounded-squircle bg-bg p-3 text-center">
                <div
                  className="mx-auto mb-1.5 h-2.5 w-2.5 rounded-full"
                  style={{ background: componentColor(value) }}
                />
                <div className="text-[11.5px] font-bold">{COMPONENT_LABELS[key]}</div>
                <div className="text-[10.5px] text-text-mute">{(value * 100).toFixed(0)}%</div>
              </div>
            ))}
          </div>

          <div className="flex gap-2.5">
            {can("manage_work_orders") && <Button onClick={raiseWorkOrder}>Raise work order</Button>}
            <Button variant="ghost" onClick={closeModal}>
              Close
            </Button>
          </div>
        </>
      )}
    </Modal>
  );
}
