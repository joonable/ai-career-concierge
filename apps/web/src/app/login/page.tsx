import { Inter, Playfair_Display } from "next/font/google";

import { LoginCard } from "@/components/auth/login-card";
import { mapLoginErrorMessage } from "@/lib/login_messages";
import { resolveSafeNextPath } from "@/lib/login_redirect";

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
          <p className={`login-hero__kicker ${bodyFont.className}`}>AI Career Concierge</p>
          <h1 className={`login-hero__headline ${headlineFont.className}`}>로그인</h1>
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
