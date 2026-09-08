import { NextResponse } from "next/server";

const BACKEND_URL = process.env.BACKEND_URL ?? "http://localhost:8000";

export async function POST(request: Request) {
  const body = await request.json();
  const upstream = await fetch(`${BACKEND_URL}/api/v1/auth/login`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(body),
    cache: "no-store",
  });
  const raw = await upstream.text();
  let payload: { detail?: string; user?: unknown; access_token?: string; refresh_token?: string; expires_in?: number };
  try { payload = raw ? JSON.parse(raw) : {}; } catch { payload = { detail: "Authentication service returned an invalid response" }; }
  if (!upstream.ok) return NextResponse.json(payload, { status: upstream.status });
  if (!payload.access_token || !payload.refresh_token || !payload.user) return NextResponse.json({ detail: "Authentication service returned an incomplete response" }, { status: 502 });
  const response = NextResponse.json({ user: payload.user });
  const secure = process.env.COOKIE_SECURE !== "false" && process.env.NODE_ENV === "production";
  response.cookies.set("flowgard_access", payload.access_token, {
    httpOnly: true, sameSite: "lax", secure, path: "/", maxAge: payload.expires_in,
  });
  response.cookies.set("flowgard_refresh", payload.refresh_token, {
    httpOnly: true, sameSite: "lax", secure, path: "/", maxAge: 60 * 60 * 24 * 7,
  });
  return response;
}
