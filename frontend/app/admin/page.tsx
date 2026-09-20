"use client";

import { FormEvent, useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAppContext } from "@/context/AppContext";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { api, type AuditEvent, type ManagedUser } from "@/lib/resources";

export default function AdminPage() {
  const { user, showToast } = useAppContext();
  const router = useRouter();
  const [items, setItems] = useState<ManagedUser[]>([]);
  const [audit, setAudit] = useState<AuditEvent[]>([]);
  const [form, setForm] = useState({ email: "", full_name: "", password: "", role: "viewer" });
  const load = useCallback(() => api<ManagedUser[]>("/users").then(setItems).catch((e: Error) => showToast(e.message)), [showToast]);
  const loadAudit = useCallback(() => api<AuditEvent[]>("/audit-events").then(setAudit).catch((e: Error) => showToast(e.message)), [showToast]);
  useEffect(() => {
    if (user?.role !== "admin") { router.replace("/"); return; }
    const timer = window.setTimeout(() => { void load(); void loadAudit(); }, 0);
    return () => window.clearTimeout(timer);
  }, [user, router, load, loadAudit]);
  async function create(event: FormEvent) {
    event.preventDefault();
    try { await api("/users", { method: "POST", body: JSON.stringify(form) }); setForm({ email: "", full_name: "", password: "", role: "viewer" }); showToast("User created"); await load(); }
    catch (e) { showToast((e as Error).message); }
  }
  async function toggle(item: ManagedUser) {
    try { await api(`/users/${item.id}`, { method: "PATCH", body: JSON.stringify({ is_active: !item.is_active }) }); showToast("User updated"); await load(); await loadAudit(); }
    catch (e) { showToast((e as Error).message); }
  }
  return <div className="animate-fade-in-up">
    <header className="mb-6"><h1>User management</h1><p className="mt-1 text-sm text-muted-foreground">Create accounts, control tenant access, and review operational changes.</p></header>
    <div className="grid gap-4 xl:grid-cols-[1fr_340px]">
      <Card padded={false}><div className="overflow-x-auto p-5"><table className="w-full"><thead><tr>{["User", "Role", "Last login", "Status", "Action"].map(h => <th key={h} className="border-b border-border px-2 py-2 text-left text-muted-foreground">{h}</th>)}</tr></thead><tbody>{items.map(item => <tr key={item.id}><td className="border-b border-border px-2 py-3"><p className="font-semibold">{item.full_name}</p><p className="text-xs text-muted-foreground">{item.email}</p></td><td className="border-b border-border px-2 py-3 capitalize">{item.role}</td><td className="border-b border-border px-2 py-3 text-sm">{item.last_login_at ? new Date(item.last_login_at).toLocaleString() : "Never"}</td><td className="border-b border-border px-2 py-3"><Badge tone={item.is_active ? "healthy" : "neutral"}>{item.is_active ? "Active" : "Disabled"}</Badge></td><td className="border-b border-border px-2 py-3"><Button size="sm" variant="ghost" disabled={item.id === user?.id} onClick={() => void toggle(item)}>{item.is_active ? "Disable" : "Enable"}</Button></td></tr>)}</tbody></table></div></Card>
      <Card><h3 className="mb-4">Add user</h3><form className="space-y-3" onSubmit={create}>{[["Full name", "full_name", "text"], ["Email", "email", "email"], ["Temporary password", "password", "password"]].map(([label, key, type]) => <label key={key} className="block text-xs font-semibold text-muted-foreground">{label}<input required type={type} value={form[key as keyof typeof form]} onChange={e => setForm({ ...form, [key]: e.target.value })} className="mt-1.5 w-full rounded-md border border-border bg-muted/50 px-3 py-2 text-sm outline-none focus:border-primary" /></label>)}<label className="block text-xs font-semibold text-muted-foreground">Role<select value={form.role} onChange={e => setForm({ ...form, role: e.target.value })} className="mt-1.5 w-full rounded-md border border-border bg-muted/50 px-3 py-2 text-sm">{["viewer", "technician", "planner", "admin"].map(role => <option key={role}>{role}</option>)}</select></label><Button type="submit">Create user</Button></form></Card>
    </div>
    <Card className="mt-4"><div className="mb-3 flex items-center justify-between"><div><h3>Audit history</h3><p className="mt-1 text-xs text-muted-foreground">Recent operational changes made by tenant users.</p></div><Badge tone="neutral">{audit.length} events</Badge></div><div className="overflow-x-auto"><table className="w-full"><thead><tr>{["Event", "Action", "Actor", "Time"].map(h => <th key={h} className="border-b border-border px-2 py-2 text-left text-xs text-muted-foreground">{h}</th>)}</tr></thead><tbody>{audit.map(event => <tr key={event.id}><td className="border-b border-border px-2 py-3 text-sm">{event.entity_reference}</td><td className="border-b border-border px-2 py-3 text-sm capitalize">{event.action}</td><td className="border-b border-border px-2 py-3 text-sm">{event.actor_email ?? "System"}</td><td className="border-b border-border px-2 py-3 text-sm">{new Date(event.created_at).toLocaleString()}</td></tr>)}</tbody></table>{audit.length === 0 && <p className="py-6 text-center text-sm text-muted-foreground">No audit events yet.</p>}</div></Card>
  </div>;
}
