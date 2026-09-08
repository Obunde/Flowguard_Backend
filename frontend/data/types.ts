export interface Station {
  code: string;
  name: string;
  lat: number;
  lon: number;
  km_from_mombasa: number;
  pump_count: number;
  max_risk: number;
  alert: boolean;
}

export interface ShapFeature {
  feature: string;
  value: number;
}

export interface ComponentStates {
  bearing: number;
  impeller: number;
  seal: number;
}

export interface Sensors {
  vibration_g: number;
  temperature_c: number;
  pressure_bar: number;
  motor_current_a: number;
}

export interface Pump {
  id?: string;
  station_id?: string;
  pump_id: string;
  station_code: string;
  risk_probability: number;
  health_deviation_index: number;
  sensors: Sensors;
  rul_hours: number | null;
  rul_ci_low: number | null;
  rul_ci_high: number | null;
  shap_top_features: ShapFeature[];
  component_states: ComponentStates;
  actual_will_fail: boolean;
  actual_failure_mode: string | null;
}

export interface ModelMetrics {
  classification_accuracy: number;
  classification_sensitivity: number;
  confusion_matrix: [[number, number], [number, number]];
  rul_mae_hours: number;
}

export interface Snapshot {
  generated_at: string;
  model_metrics: ModelMetrics;
  stations: Station[];
  pumps: Pump[];
}

export type RiskLevel = "critical" | "watch" | "healthy";

export interface CurrentUser {
  id: string;
  tenant_id: string;
  email: string;
  full_name: string;
  role: "admin" | "planner" | "technician" | "viewer";
  is_active: boolean;
  permissions: string[];
}

export interface Capabilities {
  dashboard: boolean;
  assets: boolean;
  demo_analytics: boolean;
  live_telemetry: boolean;
  live_rul: boolean;
  automatic_alerts: boolean;
  automatic_scheduling: boolean;
  smtp_digest: boolean;
  admin_console: boolean;
  data_mode: string;
}

export interface AppData {
  generated_at: string | null;
  data_mode: string;
  freshness_status: string;
  model_metrics: ModelMetrics;
  stations: Station[];
  pumps: Pump[];
  capabilities: Capabilities;
  user: CurrentUser;
}
