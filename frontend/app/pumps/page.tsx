import { Suspense } from "react";
import { PumpFleetView } from "@/components/pumps/PumpFleetView";

export default function PumpsPage() {
  return (
    <Suspense fallback={null}>
      <PumpFleetView />
    </Suspense>
  );
}
