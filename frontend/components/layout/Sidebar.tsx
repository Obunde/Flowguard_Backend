"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useAppContext } from "@/context/AppContext";
import { Icon, type IconName } from "@/components/ui/Icon";
import { cx } from "@/lib/utils";

type Item = { href: string; label: string; icon: IconName; badge?: number; permission?: string };

export function Sidebar() {
  const pathname = usePathname();
  const router = useRouter();
  const { atRiskPumps, user, can, clearSession } = useAppContext();
  const groups: Array<{ label?: string; items: Item[] }> = [
    { items: [{ href: "/", label: "Control room", icon: "dashboard" }] },
    { label: "Monitoring", items: [{ href: "/network", label: "Pipeline network", icon: "network", permission: "view_operations" }, { href: "/pumps", label: "Pump fleet", icon: "pump", permission: "view_operations" }, { href: "/flowgard", label: "Flowgard engine", icon: "engine", permission: "view_operations" }, { href: "/alerts", label: "Active alerts", icon: "alert", badge: atRiskPumps.length, permission: "view_operations" }] },
    { label: "Maintenance", items: [{ href: "/workorders", label: "Work orders", icon: "work", permission: "view_operations" }, { href: "/schedule", label: "Service schedule", icon: "calendar", permission: "manage_schedule" }] },
    { label: "Analytics", items: [{ href: "/ingestion", label: "Data operations", icon: "model", permission: "manage_models" },{ href: "/maintenance-results", label: "Maintenance outcomes", icon: "model", permission: "export_reports" },{ href: "/model", label: "Model performance", icon: "model", permission: "view_operations" }, { href: "/model/governance", label: "Model governance", icon: "settings" as IconName, permission: "run_models" }] },
    { label: "Administration", items: [{ href: "/assets", label: "Asset registry", icon: "pump" as IconName, permission: "manage_assets" }, { href: "/admin", label: "User management", icon: "users" as IconName, permission: "manage_users" }, { href: "/settings", label: "Settings", icon: "settings" as IconName, permission: "manage_tenant" }].filter((item) => !item.permission || can(item.permission)) },
  ];

  async function logout() {
    await fetch("/api/auth/logout", { method: "POST" }).catch(() => undefined);
    clearSession();
    router.replace("/login");
  }

  return <aside className="scroll-thin flex h-full w-64 shrink-0 flex-col overflow-y-auto border-r border-sidebar-border bg-sidebar p-3 text-sidebar-foreground">
    <div className="mb-3 flex items-center gap-2.5 px-2 py-3">
      <div className="flex h-8 w-8 items-center justify-center rounded-md bg-sidebar-primary text-xs font-black text-white">FG</div>
      <div><p className="text-sm font-bold leading-none">Flowgard</p><p className="mt-1 text-[10px] text-sidebar-muted">Liquid Asset Intelligence</p></div>
    </div>
    <nav className="flex-1 space-y-3">
      {groups.map((group, index) => <section key={index}>
        {group.label && <p className="mb-1.5 px-2 text-[10px] font-semibold uppercase tracking-wider text-sidebar-muted">{group.label}</p>}
        <div className="space-y-0.5">{group.items.filter((item) => !item.permission || can(item.permission)).map((item) => {
          const active = pathname === item.href;
          return <Link key={item.href} href={item.href} className={cx("flex items-center justify-between rounded-md px-2.5 py-2 text-[13px] font-medium transition-colors", active ? "bg-sidebar-accent text-white" : "text-sidebar-muted hover:bg-sidebar-accent/60 hover:text-white") }>
            <span className="flex items-center gap-2.5"><Icon name={item.icon} className={cx("h-[18px] w-[18px]", active && "text-sidebar-primary")} />{item.label}</span>
            {!!item.badge && <span className="rounded-full bg-status-critical px-1.5 text-[9px] font-bold text-white">{item.badge}</span>}
          </Link>;
        })}</div>
      </section>)}
    </nav>
    <div className="mt-3 flex items-center gap-2.5 border-t border-sidebar-border px-1 pt-3">
      <div className="flex h-8 w-8 items-center justify-center rounded-full bg-sidebar-primary/20 text-[11px] font-bold text-sidebar-primary">{user?.full_name?.[0] ?? "F"}</div>
      <div className="min-w-0 flex-1"><p className="truncate text-xs font-semibold">{user?.email}</p><p className="text-[10px] capitalize text-sidebar-muted">{user?.role}</p></div>
      <button onClick={logout} title="Sign out" className="rounded-md p-2 text-sidebar-muted hover:bg-sidebar-accent hover:text-sidebar-primary"><Icon name="logout" className="h-4 w-4" /></button>
    </div>
  </aside>;
}
