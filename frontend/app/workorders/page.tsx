"use client";

import { useCallback, useEffect, useState } from "react";
import { useAppContext } from "@/context/AppContext";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { Icon } from "@/components/ui/Icon";
import { api, download, type WorkOrder } from "@/lib/resources";

export default function WorkOrdersPage() {
  const { pumps, stationName, openPump, showToast, can, user } = useAppContext();
  const [items, setItems] = useState<WorkOrder[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [activeId, setActiveId] = useState<string | null>(null);
  const [note, setNote] = useState("");
  const [outcome, setOutcome] = useState("confirmed_failure");
  const [condition, setCondition] = useState("serviceable");

  const load = useCallback(async () => {
    try { setItems(await api<WorkOrder[]>("/work-orders")); setError(null); }
    catch (e) { setError((e as Error).message); }
  }, []);
  useEffect(() => { const timer = window.setTimeout(() => void load(), 0); return () => window.clearTimeout(timer); }, [load]);

  async function assignToMe(item: WorkOrder) {
    if (!user) return;
    try {
      await api(`/work-orders/${item.id}`, { method: "PATCH", body: JSON.stringify({ assigned_to_user_id: user.id }) });
      showToast(`Assigned ${item.id.slice(0, 8).toUpperCase()} to you`); await load();
    } catch (e) { showToast((e as Error).message); }
  }

  async function complete(item: WorkOrder) {
    if (item.priority === "high" && !note.trim()) { showToast("Add a completion note for high-priority work"); return; }
    try {
      await api(`/work-orders/${item.id}/outcome`, { method: "POST", body: JSON.stringify({ completion_note: note.trim(), outcome, post_maintenance_condition: condition }) });
      setActiveId(null); setNote(""); showToast("Work order completed"); await load();
    } catch (e) { showToast((e as Error).message); }
  }

  async function exportCsv() {
    try { await download("/exports/work-orders.csv", "flowgard-work-orders.csv"); showToast("CSV downloaded"); }
    catch (e) { showToast((e as Error).message); }
  }

  return <div className="animate-fade-in-up">
    <header className="mb-6 flex items-start justify-between gap-4">
      <div><h1>Work orders</h1><p className="mt-1 text-sm text-muted-foreground">Maintenance actions linked to current operational risk.</p></div>
      <Button onClick={exportCsv}><Icon name="download" className="mr-2 h-4 w-4" />Export CSV</Button>
    </header>
    {error && <p className="mb-3 text-sm text-red">Showing the last available work orders: {error}</p>}
    <Card padded={false}><div className="overflow-x-auto p-5"><table className="w-full min-w-[980px] border-collapse">
      <thead><tr>{["Reference", "Pump", "Station", "Issue", "Priority", "Due", "Status", "Owner", "Action"].map(h => <th key={h} className="border-b border-border px-2 py-2 text-left text-muted-foreground">{h}</th>)}</tr></thead>
      <tbody>{items.map(item => { const pump = pumps.find(p => p.id === item.pump_id); const terminal = item.status === "completed" || item.status === "cancelled"; return <tr key={item.id} className="border-b border-border/60 hover:bg-muted/40">
        <td className="px-2 py-3 font-mono text-xs">{`WO-${item.id.slice(0, 8).toUpperCase()}`}</td>
        <td className="px-2 py-3 font-semibold"><button onClick={() => pump && openPump(pump.pump_id)}>{pump?.pump_id ?? "Unknown pump"}</button></td>
        <td className="px-2 py-3">{pump ? stationName(pump.station_code) : "Unknown station"}</td>
        <td className="max-w-xs px-2 py-3">{item.title}<div className="mt-1 text-xs text-muted-foreground">{item.source_prediction_id || item.source_alert_id ? "Linked to predictive evidence" : "Manual maintenance"}</div></td>
        <td className="px-2 py-3"><Badge tone={item.priority === "high" ? "critical" : "watch"}>{item.priority}</Badge></td>
        <td className="px-2 py-3">{item.due_at ? new Date(item.due_at).toLocaleDateString() : "Unscheduled"}</td>
        <td className="px-2 py-3"><Badge tone={terminal ? "healthy" : "info"}>{item.status.replace("_", " ")}</Badge></td>
        <td className="px-2 py-3 text-xs">{item.assigned_to_user_id ? (item.assigned_to_user_id === user?.id ? "You" : "Assigned") : "Unassigned"}</td>
        <td className="px-2 py-3">{!terminal && can("manage_work_orders") ? <div className="flex items-center gap-2"><Button size="sm" variant="ghost" onClick={() => assignToMe(item)} disabled={item.assigned_to_user_id === user?.id}>Assign to me</Button><Button size="sm" onClick={() => { setActiveId(activeId === item.id ? null : item.id); setNote(item.completion_note ?? ""); }}>{activeId === item.id ? "Cancel" : "Complete"}</Button></div> : "—"}</td>
        {activeId === item.id && <td colSpan={9} className="bg-muted/30 px-2 py-3"><div className="flex items-end gap-3"><label className="flex-1 text-xs font-semibold text-muted-foreground">Completion note{item.priority === "high" ? " (required)" : ""}<textarea value={note} onChange={e => setNote(e.target.value)} rows={2} className="mt-1 block w-full rounded-md border border-border bg-background px-3 py-2 text-sm font-normal text-foreground outline-none focus:border-primary" placeholder="What was inspected or repaired?" /></label><Button onClick={() => complete(item)}>Confirm completion</Button></div></td>}
      </tr>; })}</tbody>
    </table>{items.length === 0 && <p className="py-10 text-center text-sm text-muted-foreground">No work orders.</p>}</div></Card>
  </div>;
}
