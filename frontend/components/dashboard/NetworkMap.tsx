"use client";

import { useEffect, useRef } from "react";
import type * as LeafletType from "leaflet";
import "leaflet/dist/leaflet.css";
import { useRouter } from "next/navigation";
import { useAppContext } from "@/context/AppContext";
import { riskColorVar } from "@/lib/utils";

const TILE = {
  url: "https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png",
  attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
};

export function NetworkMap() {
  const containerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<LeafletType.Map | null>(null);
  const { stations } = useAppContext();
  const router = useRouter();

  useEffect(() => {
    if (!containerRef.current || mapRef.current || stations.length === 0) return;
    let disposed = false;
    import("leaflet").then((L) => {
      if (disposed || !containerRef.current || mapRef.current) return;
      const points = stations.filter((station) => station.lat !== 0 || station.lon !== 0);
      const map = L.map(containerRef.current, { scrollWheelZoom: false }).setView([-1.7, 37.3], 6);
      L.tileLayer(TILE.url, { attribution: TILE.attribution, maxZoom: 18 }).addTo(map);
      mapRef.current = map;
      if (points.length > 1) {
        L.polyline(points.slice().sort((a, b) => a.km_from_mombasa - b.km_from_mombasa).map((s) => [s.lat, s.lon] as [number, number]), { color: "#668798", weight: 5, opacity: 0.8, lineCap: "round" }).addTo(map);
      }
      for (const station of points) {
        const marker = L.circleMarker([station.lat, station.lon], { radius: station.alert ? 10 : 8, color: "#fff", weight: 2, fillColor: riskColorVar(station.max_risk), fillOpacity: 1 }).addTo(map);
        marker.bindPopup(`<strong>${station.code} — ${station.name}</strong><br/>${station.pump_count} pumps<br/>Highest risk: ${(station.max_risk * 100).toFixed(1)}%`);
        marker.on("click", () => router.push(`/pumps?station=${encodeURIComponent(station.code)}`));
      }
      if (points.length > 1) map.fitBounds(points.map((s) => [s.lat, s.lon] as [number, number]), { padding: [28, 28] });
      window.setTimeout(() => map.invalidateSize(), 100);
    });
    return () => { disposed = true; mapRef.current?.remove(); mapRef.current = null; };
  }, [router, stations]);

  return <div className="relative overflow-hidden rounded-squircle-lg border border-border bg-muted"><div ref={containerRef} className="h-[430px] w-full" /><div className="pointer-events-none absolute right-4 top-4 rounded-squircle bg-white/90 px-3 py-2 text-[11px] shadow-soft backdrop-blur-sm"><p className="font-bold text-text">Geographic network</p><p className="text-text-mute">Click a station to view its pumps</p></div></div>;
}
