import type { AppData, Capabilities, CurrentUser, Pump, Station } from "@/data/types";
import { SNAP } from "@/data/mockData";

interface BackendDashboard {
  generated_at: string | null;
  data_mode?: string;
  freshness_status?: string;
  latest_sensor_at?: string | null;
  latest_prediction_at?: string | null;
  stations: Array<{
    code: string;
    name: string;
    lat: number | null;
    lon: number | null;
    pump_count: number;
    max_risk: number;
    alert: boolean;
  }>;
  pumps: Array<{
    id: string;
    station_id: string;
    pump_id: string;
    station_code: string;
    risk_probability: number;
    predicted_class: string | null;
    health_deviation_index: number;
    sensors: {
      vibration_g: number | null;
      temperature_c: number | null;
      pressure_kpa: number | null;
      motor_current_a: number | null;
    };
    rul_days: number | null;
    rul_ci_low_days: number | null;
    rul_ci_high_days: number | null;
    shap_top_features: Array<{ feature: string; value: number }>;
    component_states: Record<string, number>;
  }>;
  model_metrics: {
    classification_accuracy: number | null;
    classification_sensitivity: number | null;
    confusion_matrix: number[][] | null;
    rul_mae_hours: number | null;
  };
}

const FALLBACK_CAPABILITIES: Capabilities = {
  dashboard: true,
  assets: true,
  demo_analytics: true,
  live_telemetry: false,
  live_rul: false,
  automatic_alerts: false,
  automatic_scheduling: false,
  smtp_digest: false,
  admin_console: true,
  data_mode: "demo_snapshot",
};

export async function loadAppData(): Promise<AppData> {
  const dashboard = SNAP as unknown as BackendDashboard;
  const capabilities = FALLBACK_CAPABILITIES;
  const user: CurrentUser = {
    id: "mock-user-id",
    email: "admin@flowgard.com",
    role: "admin",
    tenant_id: "KPC",
    full_name: "Mock Admin",
    is_active: true,
    permissions: []
  };
  const stations: Station[] = dashboard.stations.map((station) => ({
    code: station.code,
    name: station.name,
    lat: station.lat ?? 0,
    lon: station.lon ?? 0,
    km_from_mombasa: 0,
    pump_count: station.pump_count,
    max_risk: station.max_risk,
    alert: station.alert,
  }));
  const pumps: Pump[] = dashboard.pumps.map((pump) => ({
    id: pump.id,
    station_id: pump.station_id,
    pump_id: pump.pump_id,
    station_code: pump.station_code,
    risk_probability: pump.risk_probability,
    health_deviation_index: pump.health_deviation_index,
    sensors: {
      vibration_g: pump.sensors.vibration_g ?? 0,
      temperature_c: pump.sensors.temperature_c ?? 0,
      pressure_bar: (pump.sensors.pressure_kpa ?? 0) / 100,
      motor_current_a: pump.sensors.motor_current_a ?? 0,
    },
    rul_hours: pump.rul_days === null ? null : pump.rul_days * 24,
    rul_ci_low: pump.rul_ci_low_days === null ? null : pump.rul_ci_low_days * 24,
    rul_ci_high: pump.rul_ci_high_days === null ? null : pump.rul_ci_high_days * 24,
    shap_top_features: pump.shap_top_features,
    component_states: {
      bearing: pump.component_states.bearing ?? 0,
      impeller: pump.component_states.impeller ?? 0,
      seal: pump.component_states.seal ?? 0,
    },
    actual_will_fail: false,
    actual_failure_mode: pump.predicted_class,
  }));
  return {
    generated_at: dashboard.generated_at,
    data_mode: dashboard.data_mode ?? capabilities.data_mode,
    freshness_status: dashboard.freshness_status ?? "demo",
    stations,
    pumps,
    model_metrics: {
      classification_accuracy: dashboard.model_metrics.classification_accuracy ?? 0,
      classification_sensitivity: dashboard.model_metrics.classification_sensitivity ?? 0,
      confusion_matrix: (dashboard.model_metrics.confusion_matrix ?? [[0, 0], [0, 0]]) as [[number, number], [number, number]],
      rul_mae_hours: dashboard.model_metrics.rul_mae_hours ?? 0,
    },
    capabilities,
    user,
  };
}
