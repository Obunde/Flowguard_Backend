import { cookies } from "next/headers";
import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL = process.env.BACKEND_URL ?? "http://localhost:8000";

interface RouteContext { params: Promise<{ path: string[] }> }

async function refreshAccess(refreshToken: string) {
  const response = await fetch(`${BACKEND_URL}/api/v1/auth/refresh`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ refresh_token: refreshToken }),
    cache: "no-store",
  });
  if (!response.ok) return null;
  return response.json();
}

async function proxy(request: NextRequest, context: RouteContext) {
  const { path } = await context.params;
  const cookieStore = await cookies();
  const accessToken = cookieStore.get("flowgard_access")?.value;
  const refreshToken = cookieStore.get("flowgard_refresh")?.value;
  const target = `${BACKEND_URL}/${path.join("/")}${request.nextUrl.search}`;
  const body = request.method === "GET" || request.method === "HEAD" ? undefined : await request.text();
  const send = (token?: string) => fetch(target, {
    method: request.method,
    headers: {
      ...(request.headers.get("content-type") ? { "content-type": request.headers.get("content-type")! } : {}),
      ...(token ? { authorization: `Bearer ${token}` } : {}),
    },
    body,
    cache: "no-store",
  });
  let upstream = await send(accessToken);
  let rotated: Awaited<ReturnType<typeof refreshAccess>> = null;
  if (upstream.status === 401 && refreshToken) {
    rotated = await refreshAccess(refreshToken);
    if (rotated) upstream = await send(rotated.access_token);
  }
  const response = new NextResponse(await upstream.arrayBuffer(), {
    status: upstream.status,
    headers: { "content-type": upstream.headers.get("content-type") ?? "application/json" },
  });
  if (rotated) {
    const secure = process.env.COOKIE_SECURE !== "false" && process.env.NODE_ENV === "production";
    response.cookies.set("flowgard_access", rotated.access_token, {
      httpOnly: true, sameSite: "lax", secure, path: "/", maxAge: rotated.expires_in,
    });
    response.cookies.set("flowgard_refresh", rotated.refresh_token, {
      httpOnly: true, sameSite: "lax", secure, path: "/", maxAge: 60 * 60 * 24 * 7,
    });
  }
  return response;
}

export const GET = proxy;
export const POST = proxy;
export const PATCH = proxy;
export const PUT = proxy;
export const DELETE = proxy;
