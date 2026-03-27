import { NextResponse, type NextRequest } from "next/server";

import { resolvePostLoginPath, resolveSafeNextPath } from "@/lib/login_redirect";
import { createSupabaseRouteHandlerClient } from "@/lib/supabase_auth_server";

export async function GET(request: NextRequest) {
  const requestUrl = new URL(request.url);
  const code = requestUrl.searchParams.get("code");
  const nextPath = resolveSafeNextPath(requestUrl.searchParams.get("next"));

  if (!code) {
    const loginUrl = new URL("/login", request.url);
    loginUrl.searchParams.set("error", "missing_code");
    return NextResponse.redirect(loginUrl);
  }

  const response = new NextResponse(null, { status: 200 });
  const supabase = await createSupabaseRouteHandlerClient(request, response);
  const {
    data: { session },
    error,
  } = await supabase.auth.exchangeCodeForSession(code);

  if (error) {
    const loginUrl = new URL("/login", request.url);
    loginUrl.searchParams.set("error", "callback_failed");
    if (nextPath) {
      loginUrl.searchParams.set("next", nextPath);
    }
    return NextResponse.redirect(loginUrl);
  }

  const destination = session?.access_token
    ? await resolvePostLoginPath(session.access_token, nextPath)
    : "/onboarding";
  const redirectResponse = NextResponse.redirect(new URL(destination, request.url));

  response.cookies.getAll().forEach((cookie) => {
    redirectResponse.cookies.set(cookie);
  });

  return redirectResponse;
}
