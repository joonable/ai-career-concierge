import type { NextRequest } from "next/server";
import { NextResponse } from "next/server";

import { createSupabaseMiddlewareClient } from "@/lib/supabase_auth_middleware";

const PROTECTED_PATHS = ["/onboarding", "/dashboard"];

export async function middleware(request: NextRequest) {
  const isProtected = PROTECTED_PATHS.some((path) =>
    request.nextUrl.pathname.startsWith(path),
  );

  if (!isProtected) {
    return NextResponse.next();
  }

  const response = NextResponse.next({
    request: {
      headers: request.headers,
    },
  });
  const supabase = createSupabaseMiddlewareClient(request, response);
  const {
    data: { session },
  } = await supabase.auth.getSession();

  if (session) {
    return response;
  }

  const loginUrl = new URL("/login", request.url);
  loginUrl.searchParams.set("next", request.nextUrl.pathname);
  return NextResponse.redirect(loginUrl);
}

export const config = {
  matcher: ["/onboarding/:path*", "/dashboard/:path*"],
};
