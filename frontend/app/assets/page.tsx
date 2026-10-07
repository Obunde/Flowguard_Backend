"use client";
import { useEffect, useMemo, useState } from "react";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { api } from "@/lib/resources";
type Asset={asset_type:string;asset_key:string;name:string;region:string|null;status:string;parent_key:string|null};
function renderStatus(status: string) {
  const s = status.toLowerCase().replace(/_/g, " ");
  if (s === "operational" || s === "active" || s === "running") {
    return <Badge tone="healthy">Operational</Badge>;
  }
  if (s === "needs maintenance" || s === "needs_maintenance" || s === "attention needed") {
    return <Badge tone="watch">Needs Maintenance</Badge>;
  }
  if (s === "maintenance" || s === "in maintenance") {
    return <Badge tone="watch">In Maintenance</Badge>;
  }
  if (s === "kept for future use" || s === "future use" || s === "standby" || s === "reserved") {
    return <Badge tone="neutral">Kept for Future Use</Badge>;
  }
  if (s === "decommissioned" || s === "inactive") {
    return <Badge tone="neutral">Decommissioned</Badge>;
  }
  return <Badge tone="neutral">{s}</Badge>;
}

export default function AssetsPage(){const [items,setItems]=useState<Asset[]>([]);const [error,setError]=useState<string|null>(null);const [filter,setFilter]=useState("all");useEffect(()=>{void api<Asset[]>("/assets").then(setItems).catch((e:Error)=>setError(e.message))},[]);const visible=useMemo(()=>filter==="all"?items:items.filter(item=>item.asset_type===filter),[items,filter]);return <div className="animate-fade-in-up"><header className="mb-6"><h1>Asset registry</h1><p className="mt-1 text-sm text-muted-foreground">The master inventory and hierarchy of stations and pumps. Use the Control room and Pump fleet pages for health, risk, and maintenance actions.</p></header><Card className="mb-4 bg-muted/30"><div className="grid gap-3 md:grid-cols-2"><div><p className="text-sm font-semibold">Asset registry</p><p className="mt-1 text-xs text-muted-foreground">What exists, where it is, who owns it, and its lifecycle status.</p></div><div><p className="text-sm font-semibold">Operational views</p><p className="mt-1 text-xs text-muted-foreground">What is happening now: predictive risk, alerts, work orders, schedules, and outcomes.</p></div></div></Card>{error&&<p className="mb-4 text-sm text-red">Unable to load assets: {error}</p>}<div className="mb-3 flex gap-2"><button onClick={()=>setFilter("all")} className="rounded border border-border px-3 py-1 text-xs">All</button><button onClick={()=>setFilter("station")} className="rounded border border-border px-3 py-1 text-xs">Stations</button><button onClick={()=>setFilter("pump")} className="rounded border border-border px-3 py-1 text-xs">Pumps</button></div><Card padded={false}><div className="overflow-x-auto p-5"><table className="w-full"><thead><tr>{["Type","Asset","Parent","Region","Lifecycle status"].map(h=><th key={h} className="border-b border-border px-2 py-2 text-left text-xs text-muted-foreground">{h}</th>)}</tr></thead><tbody>{visible.map(item=><tr key={`${item.asset_type}-${item.asset_key}`}><td className="border-b border-border px-2 py-3 capitalize">{item.asset_type}</td><td className="border-b border-border px-2 py-3 font-semibold">{item.name}</td><td className="border-b border-border px-2 py-3">{item.parent_key??"Top level"}</td><td className="border-b border-border px-2 py-3">{item.region??"Unassigned"}</td><td className="border-b border-border px-2 py-3">{renderStatus(item.status)}</td></tr>)}</tbody></table>{visible.length===0&&<p className="py-10 text-center text-sm text-muted-foreground">No assets configured.</p>}</div></Card></div>}