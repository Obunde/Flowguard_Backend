import type { Pump } from "@/data/types";
import { CRIT, WARN } from "@/lib/utils";

export const selectAtRiskPumps = (pumps: Pump[]) =>
  pumps.filter((p) => p.risk_probability > WARN).sort((a, b) => b.risk_probability - a.risk_probability);

export const selectCriticalPumps = (pumps: Pump[]) => pumps.filter((p) => p.risk_probability > CRIT);

export const selectWatchPumps = (pumps: Pump[]) => selectAtRiskPumps(pumps).filter((p) => p.risk_probability <= CRIT);

export const selectHealthyPumps = (pumps: Pump[]) => pumps.filter((p) => p.risk_probability <= WARN);
