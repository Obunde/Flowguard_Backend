import { cookies } from "next/headers";
import { NextResponse } from "next/server";

const BACKEND_URL = process.env.BACKEND_URL ?? "http://localhost:8000";

export async function POST() {
  const store = await cookies();
  const refreshToken = store.get("flowgard_refresh")?.value;
  if (refreshToken) {
    await fetch(`${BACKEND_URL}/api/v1/auth/logout`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ refresh_token: refreshToken }),
      cache: "no-store",
    }).catch(() => undefined);
  }
  const response = NextResponse.json({ logged_out: true });
  response.cookies.set("flowgard_access", "", { maxAge: 0, path: "/" });
  response.cookies.set("flowgard_refresh", "", { maxAge: 0, path: "/" });
  return response;
}
