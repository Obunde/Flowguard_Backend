export interface WorkOrder { id: string; pump_id: string; station_id: string; title: string; description: string | null; priority: string; due_at: string | null; status: string; source: string; assigned_to_user_id: string | null; source_alert_id: string | null; source_prediction_id: string | null; completion_note: string | null; root_cause: string | null; corrective_action: string | null; downtime_minutes: number | null; follow_up_required: boolean; closed_at: string | null; }
export interface Alert { id: string; pump_id: string; station_id: string; severity: "info" | "warning" | "critical"; status: "triggered" | "acknowledged" | "resolved"; message: string; triggered_at: string; source: string | null; }
export interface ScheduleEntry { id: string; pump_id: string; station_id: string; work_order_id: string | null; scheduled_date: string; priority_rank: number | null; status: string; created_from: string | null; }
export interface TenantSettings { id: string; name: string; slug: string; fluid_type: string; pressure_threshold_kpa: number; vibration_threshold_mm_s: number; branding_display_name: string | null; branding_primary_color: string | null; is_active: boolean; }
export interface AuditEvent { id: string; entity_type: string; entity_reference: string; action: string; actor_email: string | null; previous_value: Record<string, unknown> | null; new_value: Record<string, unknown> | null; created_at: string; }
export interface ManagedUser { id: string; email: string; full_name: string; role: string; is_active: boolean; last_login_at: string | null; }

export async function api<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`/api/backend/api/v1${path}`, { cache: "no-store", ...init, headers: { ...(init?.body ? { "content-type": "application/json" } : {}), ...init?.headers } });
  if (!response.ok) { const payload = await response.json().catch(() => null) as { detail?: string } | null; throw new Error(payload?.detail ?? `Request failed (${response.status})`); }
  return response.json() as Promise<T>;
}

export async function download(path: string, filename: string) {
  const response = await fetch(`/api/backend/api/v1${path}`);
  if (!response.ok) throw new Error("Export failed");
  const url = URL.createObjectURL(await response.blob());
  const anchor = document.createElement("a"); anchor.href = url; anchor.download = filename; anchor.click(); URL.revokeObjectURL(url);
}
