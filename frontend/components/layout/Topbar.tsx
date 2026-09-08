"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { useAppContext } from "@/context/AppContext";
import { Icon } from "@/components/ui/Icon";

export function Topbar() {
  const { openPump, pumps, stations, atRiskPumps, lastUpdated, freshnessStatus, user } = useAppContext();
  const router = useRouter();
  const [query, setQuery] = useState("");
  function search(value: string) {
    setQuery(value);
    if (value.trim().length < 2) return;
    const term = value.trim().toLowerCase();
    const pump = pumps.find((item) => item.pump_id.toLowerCase().includes(term));
    if (pump) return openPump(pump.pump_id);
    const station = stations.find((item) => item.code.toLowerCase().includes(term) || item.name.toLowerCase().includes(term));
    if (station) router.push(`/pumps?station=${encodeURIComponent(station.code)}`);
  }
  return <header className="flex h-14 shrink-0 items-center justify-between gap-4 border-b border-border bg-background/80 px-6 backdrop-blur-md">
    <label className="flex w-full max-w-md items-center gap-2 rounded-md border border-border bg-muted/60 px-3 py-1.5 text-muted-foreground">
      <Icon name="search" className="h-4 w-4 shrink-0" />
      <input value={query} onChange={(event) => search(event.target.value)} aria-label="Search pumps and stations" placeholder="Search pumps and stations…" className="w-full bg-transparent text-xs text-foreground outline-none placeholder:text-muted-foreground" />
    </label>
    <div className="hidden items-center gap-3 text-[11px] text-muted-foreground lg:flex">
      <span className="rounded-full bg-muted px-2 py-1 font-semibold capitalize text-foreground">{user?.role ?? "workspace"} workspace</span>
      <span className={freshnessStatus === "fresh" ? "h-2 w-2 rounded-full bg-status-low" : "h-2 w-2 rounded-full bg-status-critical"} />
      <span>{freshnessStatus === "demo" ? "Demo data" : freshnessStatus === "fresh" ? "Live data" : freshnessStatus === "stale" ? "Data stale" : "Data unavailable"}</span>
      <span>{lastUpdated ? `· ${new Date(lastUpdated).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}` : ""}</span>
    </div>
    <Link href="/alerts" className="relative rounded-md p-2 text-muted-foreground transition-colors hover:bg-accent hover:text-foreground" aria-label="Active alerts">
      <Icon name="alert" className="h-[18px] w-[18px]" />
      {atRiskPumps.length > 0 && <span className="absolute right-1 top-1 flex h-3.5 min-w-3.5 items-center justify-center rounded-full bg-status-critical px-1 text-[8px] font-bold text-white">{atRiskPumps.length}</span>}
    </Link>
  </header>;
}
