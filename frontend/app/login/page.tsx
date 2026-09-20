"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { useAppContext } from "@/context/AppContext";

export default function LoginPage() {
  const router = useRouter();
  const { clearSession, refreshData } = useAppContext();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      const response = await fetch("/api/auth/login", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ email, password }),
      });
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.detail ?? "Unable to sign in");
      clearSession();
      await refreshData();
      router.push("/");
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Unable to sign in");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="flex min-h-full items-center justify-center bg-[radial-gradient(circle_at_top_left,#dff8f3,transparent_35%),radial-gradient(circle_at_bottom_right,#dceaff,transparent_30%),var(--color-bg)] p-6">
      <section className="glass-light w-full max-w-[420px] rounded-squircle p-8 shadow-elevated">
        <div className="mb-7 flex items-center gap-3">
          <div className="flex h-11 w-11 items-center justify-center rounded-squircle-sm bg-gradient-to-br from-teal to-blue text-lg text-white shadow-soft">◈</div>
          <div>
            <div className="text-sm font-extrabold tracking-wide">FLOWGARD</div>
            <div className="text-[10px] tracking-[0.12em] text-text-mute">LIQUID ASSET INTELLIGENCE</div>
          </div>
        </div>
        <h1 className="text-[28px] font-extrabold tracking-tight">Welcome back</h1>
        <p className="mt-1 text-sm text-text-mute">Sign in to the control room.</p>
        <form className="mt-7 space-y-4" onSubmit={submit}>
          <label className="block text-xs font-bold text-text-mute">
            Email
            <input
              className="mt-1.5 w-full rounded-squircle-sm border border-border bg-white/70 px-4 py-3 text-sm text-text outline-none focus:border-teal focus:ring-2 focus:ring-teal/20"
              type="email"
              autoComplete="email"
              required
              value={email}
              onChange={(event) => setEmail(event.target.value)}
            />
          </label>
          <label className="block text-xs font-bold text-text-mute">
            Password
            <input
              className="mt-1.5 w-full rounded-squircle-sm border border-border bg-white/70 px-4 py-3 text-sm text-text outline-none focus:border-teal focus:ring-2 focus:ring-teal/20"
              type="password"
              autoComplete="current-password"
              required
              value={password}
              onChange={(event) => setPassword(event.target.value)}
            />
          </label>
          {error && <p className="rounded-squircle-sm bg-red-light p-3 text-xs font-semibold text-red">{error}</p>}
          <button
            className="w-full rounded-squircle-sm bg-teal px-4 py-3 text-sm font-extrabold text-white shadow-soft transition-opacity hover:opacity-90 disabled:opacity-60"
            type="submit"
            disabled={submitting}
          >
            {submitting ? "Signing in…" : "Sign in"}
          </button>
        </form>
        <p className="mt-5 text-center text-[11px] leading-relaxed text-text-mute">
          Demo analytics are synthetic and must not be used for operational decisions.
        </p>
      </section>
    </main>
  );
}
