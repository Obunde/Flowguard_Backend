"use client";

import { usePathname, useRouter } from "next/navigation";
import { PumpModal } from "@/components/PumpModal";
import { Sidebar } from "@/components/layout/Sidebar";
import { Topbar } from "@/components/layout/Topbar";
import { Toast } from "@/components/ui/Toast";
import { useAppContext } from "@/context/AppContext";

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const { loading, error, hasData, user, can } = useAppContext();
  const requiredPermission = pathname === "/assets" ? "manage_assets" : pathname === "/schedule" ? "manage_schedule" : pathname === "/ingestion" ? "manage_models" : pathname === "/maintenance-results" ? "export_reports" : pathname === "/model/governance" ? "run_models" : pathname === "/admin" ? "manage_users" : pathname === "/settings" ? "manage_tenant" : pathname !== "/" ? "view_operations" : null;
  if (!loading && user && requiredPermission && !can(requiredPermission)) {
    router.replace("/");
    return null;
  }
  if (pathname === "/login") return <>{children}</>;
  if (loading) {
    return (
      <div className="flex h-full items-center justify-center bg-bg">
        <div className="rounded-squircle bg-surface px-6 py-5 text-sm font-semibold shadow-soft">
          Loading control room…
        </div>
      </div>
    );
  }
  if (error && !hasData) {
    return (
      <div className="flex h-full items-center justify-center bg-bg p-6">
        <div className="max-w-md rounded-squircle bg-surface p-6 text-center shadow-soft">
          <h1 className="text-lg font-extrabold">Unable to load Flowgard</h1>
          <p className="mt-2 text-sm text-text-mute">{error}</p>
          <button
            className="mt-4 rounded-squircle-sm bg-teal px-4 py-2 text-sm font-bold text-white"
            onClick={() => location.reload()}
          >
            Try again
          </button>
        </div>
      </div>
    );
  }
  return (
    <>
      <div className="flex h-full overflow-hidden">
        <Sidebar />
        <div className="flex h-full min-w-0 flex-1 flex-col overflow-hidden">
          <Topbar />
          <main className="scroll-thin flex-1 overflow-y-auto p-6">{children}</main>
        </div>
      </div>
      <Toast />
      <PumpModal />
    </>
  );
}
