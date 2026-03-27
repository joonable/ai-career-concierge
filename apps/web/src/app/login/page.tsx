import { Inter, Playfair_Display } from "next/font/google";
import { redirect } from "next/navigation";

import { LoginCard } from "@/components/auth/login-card";
import { mapLoginErrorMessage } from "@/lib/login_messages";
import { resolvePostLoginPath, resolveSafeNextPath } from "@/lib/login_redirect";
import { createSupabaseServerClient } from "@/lib/supabase_auth_server";

type LoginPageProps = {
  searchParams?: Promise<{
    error?: string;
    next?: string;
  }>;
};

const headlineFont = Playfair_Display({
  subsets: ["latin"],
  weight: "700",
});

const bodyFont = Inter({
  subsets: ["latin"],
  weight: ["400", "500", "600"],
});

export default async function LoginPage({ searchParams }: LoginPageProps) {
  const resolvedSearchParams = (await searchParams) ?? {};
  const nextPath = resolveSafeNextPath(resolvedSearchParams.next);
  const errorMessage = mapLoginErrorMessage(resolvedSearchParams.error);
  const supabase = await createSupabaseServerClient();
  const {
    data: { session },
  } = await supabase.auth.getSession();

  if (session?.access_token) {
    const destination = await resolvePostLoginPath(session.access_token, nextPath);
    redirect(destination);
  }

  return (
    <main className="woven-hero login-hero">
      <div className="woven-hero__veil" />

      <nav className="woven-nav">
        <div className="woven-nav__brand">
          <span className="woven-nav__mark" aria-hidden="true">
            ⎎
          </span>
          <span className={bodyFont.className}>AI Career Concierge</span>
        </div>
      </nav>

      <section className="login-hero__content">
        <div className="login-hero__copy">
          <p className={`login-hero__kicker ${bodyFont.className}`}>P0 Login</p>
          <h1 className={`login-hero__headline ${headlineFont.className}`}>
            Google 로그인 후 바로 첫 화면으로 연결합니다.
          </h1>
          <p className={bodyFont.className}>
            로그인 후 온보딩이 비어 있으면 기준 설정 화면으로, 이미 설정되어 있으면 추천
            대시보드로 이동합니다.
          </p>
        </div>
        <LoginCard
          bodyClassName={bodyFont.className}
          errorMessage={errorMessage}
          nextPath={nextPath ?? undefined}
        />
      </section>
    </main>
  );
}
