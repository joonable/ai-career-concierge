"use client";

import React, { startTransition, useState } from "react";

import { FeyButton } from "@/components/ui/fey-button";
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

  const handleSignIn = () => {
    setIsPending(true);
    setMessage(null);

    startTransition(async () => {
      try {
        const supabase = createSupabaseBrowserClient();
        const origin = window.location.origin;
        const redirectPath = resolveSafeNextPath(nextPath);
        const redirectUrl = new URL("/auth/callback", origin);
        if (redirectPath) {
          redirectUrl.searchParams.set("next", redirectPath);
        }
        const { error } = await supabase.auth.signInWithOAuth({
          provider: "google",
          options: {
            redirectTo: redirectUrl.toString(),
          },
        });

        if (error) {
          throw error;
        }

        setMessage("Google 로그인 페이지로 이동합니다.");
      } catch {
        setMessage("Google 로그인을 시작하지 못했습니다. 다시 시도하세요.");
      } finally {
        setIsPending(false);
      }
    });
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
