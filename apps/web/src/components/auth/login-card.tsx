"use client";

import React, { useState } from "react";

import { FeyButton } from "@/components/ui/fey-button";
import { redirectToExternalUrl } from "@/lib/browser_redirect";
import { resolveSafeNextPath } from "@/lib/login_redirect";
import { createSupabaseBrowserClient } from "@/lib/supabase_auth_browser";

type LoginCardProps = {
  bodyClassName: string;
  errorMessage?: string;
  nextPath?: string;
};

export function LoginCard({ bodyClassName, errorMessage, nextPath }: LoginCardProps) {
  const [message, setMessage] = useState<string | null>(null);
  const [isPending, setIsPending] = useState(false);

  const handleSignIn = async () => {
    setIsPending(true);
    setMessage(null);

    try {
      const supabase = createSupabaseBrowserClient();
      const origin = window.location.origin;
      const redirectPath = resolveSafeNextPath(nextPath);
      const redirectUrl = new URL("/auth/callback", origin);
      if (redirectPath) {
        redirectUrl.searchParams.set("next", redirectPath);
      }
      const {
        data: { url },
        error,
      } = await supabase.auth.signInWithOAuth({
        provider: "google",
        options: {
          redirectTo: redirectUrl.toString(),
          queryParams: {
            prompt: "select_account",
          },
          skipBrowserRedirect: true,
        },
      });

      if (error || !url) {
        throw error ?? new Error("Missing OAuth redirect URL.");
      }

      setMessage("Google 로그인 페이지로 이동합니다.");
      redirectToExternalUrl(url);
    } catch {
      setMessage("Google 로그인을 시작하지 못했습니다. 다시 시도하세요.");
      setIsPending(false);
    }
  };

  return (
    <section className="login-card">
      <div className="login-card__body">
        <h2 className={bodyClassName}>Google로 계속하기</h2>
        <p className={`login-card__status ${bodyClassName}`}>{errorMessage ?? message ?? " "}</p>
        <FeyButton disabled={isPending} onClick={handleSignIn} type="button">
          {isPending ? "Google 연결 중..." : "Continue with Google"}
        </FeyButton>
      </div>
    </section>
  );
}
