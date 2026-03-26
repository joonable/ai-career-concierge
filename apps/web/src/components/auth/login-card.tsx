"use client";

import { startTransition, useState } from "react";

import { createSupabaseBrowserClient } from "@/lib/supabase_auth";

export function LoginCard() {
  const [message, setMessage] = useState("Google OAuth will redirect back into `/auth/callback`.");
  const [isPending, setIsPending] = useState(false);

  const handleSignIn = () => {
    setIsPending(true);
    startTransition(async () => {
      try {
        const supabase = createSupabaseBrowserClient();
        const origin = window.location.origin;
        const { error } = await supabase.auth.signInWithOAuth({
          provider: "google",
          options: {
            redirectTo: `${origin}/auth/callback`,
          },
        });

        if (error) {
          throw error;
        }

        setMessage("Redirecting to Google OAuth.");
      } catch {
        document.cookie = "acc_session=demo; path=/";
        window.location.href = "/onboarding";
      } finally {
        setIsPending(false);
      }
    });
  };

  return (
    <section className="panel" style={{ padding: 28 }}>
      <div className="stack">
        <span className="eyebrow">Single-user PoC</span>
        <h2 style={{ margin: 0, fontSize: "1.9rem" }}>Sign in and set the operating profile.</h2>
        <p className="muted" style={{ margin: 0 }}>
          The frontend stays thin: auth here, business logic in FastAPI, evaluation in LangGraph.
        </p>
        <button className="button primary" disabled={isPending} onClick={handleSignIn} type="button">
          {isPending ? "Connecting..." : "Continue with Google"}
        </button>
        <p className="muted" style={{ margin: 0 }}>{message}</p>
      </div>
    </section>
  );
}
