import type { Metadata } from "next";
import "./globals.css";
import { AppProvider } from "@/context/AppContext";
import { AppShell } from "@/components/layout/AppShell";

export const metadata: Metadata = {
  title: "Flowgard — Predictive Maintenance",
  description: "Predictive maintenance and operational intelligence for liquid transport infrastructure.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="h-full antialiased">
      <body className="h-full bg-bg text-text">
        <AppProvider>
          <AppShell>{children}</AppShell>
        </AppProvider>
      </body>
    </html>
  );
}
