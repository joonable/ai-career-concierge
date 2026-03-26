import type { NextRequest } from "next/server";
import { NextResponse } from "next/server";

const PROTECTED_PATHS = ["/onboarding", "/dashboard"];

export function middleware(request: NextRequest) {
  const isProtected = PROTECTED_PATHS.some((path) =>
    request.nextUrl.pathname.startsWith(path),
  );

  if (!isProtected) {
    return NextResponse.next();
  }

  const hasSession =
    request.cookies.has("acc_session") || request.cookies.has("sb-access-token");

  if (hasSession) {
    return NextResponse.next();
  }

  const loginUrl = new URL("/login", request.url);
  loginUrl.searchParams.set("next", request.nextUrl.pathname);
  return NextResponse.redirect(loginUrl);
}

export const config = {
  matcher: ["/onboarding/:path*", "/dashboard/:path*"],
};
