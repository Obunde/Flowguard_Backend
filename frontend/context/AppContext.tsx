"use client";

import { usePathname, useRouter } from "next/navigation";
import { createContext, useCallback, useContext, useEffect, useMemo, useRef, useState, type ReactNode } from "react";
import type { AppData, Capabilities, CurrentUser, ModelMetrics, Pump, Station } from "@/data/types";
import { loadAppData } from "@/lib/api";

interface AppContextValue {
  loading: boolean;
  hasData: boolean;
  lastUpdated: string | null;
  freshnessStatus: string;
  error: string | null;
  stations: Station[];
  pumps: Pump[];
  modelMetrics: ModelMetrics;
  capabilities: Capabilities | null;
  user: CurrentUser | null;
  atRiskPumps: Pump[];
  criticalPumps: Pump[];
  healthyPumps: Pump[];
  refreshData: () => Promise<void>;
  clearSession: () => void;
  stationName: (code: string) => string;
  toastMessage: string | null;
  showToast: (message: string) => void;
  openPumpId: string | null;
  openPump: (id: string) => void;
  closeModal: () => void;
  can: (permission: string) => boolean;
}

const AppContext = createContext<AppContextValue | null>(null);

export function AppProvider({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const [data, setData] = useState<AppData | null>(null);
  const [loading, setLoading] = useState(pathname !== "/login");
  const [error, setError] = useState<string | null>(null);
  const [toastMessage, setToastMessage] = useState<string | null>(null);
  const [toastVisible, setToastVisible] = useState(false);
  const [openPumpId, setOpenPumpId] = useState<string | null>(null);
  const toastTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  const refreshData = useCallback(async () => {
    setLoading(data === null);
    setError(null);
    try {
      setData(await loadAppData());
    } catch (reason) {
      if (reason instanceof Error && reason.message === "UNAUTHENTICATED") {
        if (pathname !== "/login") router.replace("/login");
        return;
      }
      setError(reason instanceof Error ? reason.message : "Unable to load Flowgard");
    } finally {
      setLoading(false);
    }
  }, [data, pathname, router]);

  useEffect(() => {
    if (pathname === "/login" || data) return;
    const timer = window.setTimeout(() => void refreshData(), 0);
    return () => window.clearTimeout(timer);
  }, [pathname, data, refreshData]);

  useEffect(() => {
    if (pathname === "/login" || !data) return;
    const timer = window.setInterval(() => void refreshData(), 15000);
    return () => window.clearInterval(timer);
  }, [pathname, data, refreshData]);

  const showToast = useCallback((message: string) => {
    if (toastTimer.current) clearTimeout(toastTimer.current);
    setToastMessage(message);
    setToastVisible(true);
    toastTimer.current = setTimeout(() => setToastVisible(false), 2600);
  }, []);

  const openPump = useCallback((id: string) => {
    if (!data?.pumps.find((pump) => pump.pump_id === id)) return;
    setOpenPumpId(id);
  }, [data]);

  const closeModal = useCallback(() => setOpenPumpId(null), []);
  const clearSession = useCallback(() => {
    setData(null);
    setError(null);
    setOpenPumpId(null);
    setLoading(false);
  }, []);
  const can = useCallback((permission: string) => data?.user.permissions.includes(permission) ?? false, [data]);

  const pumps = useMemo(() => data?.pumps ?? [], [data]);
  const stations = useMemo(() => data?.stations ?? [], [data]);
  const atRiskPumps = useMemo(
    () => pumps.filter((pump) => pump.risk_probability > 0.15).sort((a, b) => b.risk_probability - a.risk_probability),
    [pumps]
  );
  const criticalPumps = useMemo(() => pumps.filter((pump) => pump.risk_probability > 0.5), [pumps]);
  const healthyPumps = useMemo(() => pumps.filter((pump) => pump.risk_probability <= 0.15), [pumps]);
  const stationName = useCallback(
    (code: string) => stations.find((station) => station.code === code)?.name ?? code,
    [stations]
  );

  const value = useMemo(
    () => ({
      loading,
      hasData: data !== null,
      lastUpdated: data?.generated_at ?? null,
      freshnessStatus: data?.freshness_status ?? "unavailable",
      error,
      stations,
      pumps,
      modelMetrics: data?.model_metrics ?? { classification_accuracy: 0, classification_sensitivity: 0, confusion_matrix: [[0, 0], [0, 0]], rul_mae_hours: 0 },
      capabilities: data?.capabilities ?? null,
      user: data?.user ?? null,
      atRiskPumps,
      criticalPumps,
      healthyPumps,
      refreshData,
      clearSession,
      stationName,
      toastMessage: toastVisible ? toastMessage : null,
      showToast,
      openPumpId,
      openPump,
      closeModal,
      can,
    }),
    [loading, error, stations, pumps, data, atRiskPumps, criticalPumps, healthyPumps, refreshData, clearSession, stationName, toastMessage, toastVisible, showToast, openPumpId, openPump, closeModal, can]
  );

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
}

export function useAppContext() {
  const ctx = useContext(AppContext);
  if (!ctx) throw new Error("useAppContext must be used within AppProvider");
  return ctx;
}
