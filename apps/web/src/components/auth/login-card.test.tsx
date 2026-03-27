import React from "react";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi, beforeEach } from "vitest";

import { LoginCard } from "@/components/auth/login-card";

const signInWithOAuth = vi.fn();

vi.mock("@/lib/supabase_auth_browser", () => ({
  createSupabaseBrowserClient: () => ({
    auth: {
      signInWithOAuth,
    },
  }),
}));

describe("LoginCard", () => {
  beforeEach(() => {
    signInWithOAuth.mockReset();
    window.history.replaceState({}, "", "http://localhost:3000/login");
  });

  it("calls Google OAuth with the provided next path", async () => {
    signInWithOAuth.mockResolvedValue({ error: null });
    const user = userEvent.setup();

    render(<LoginCard bodyClassName="body" nextPath="/dashboard" />);

    await user.click(screen.getByRole("button", { name: "Continue with Google" }));

    await waitFor(() => {
      expect(signInWithOAuth).toHaveBeenCalledWith({
        provider: "google",
        options: {
          redirectTo: "http://localhost:3000/auth/callback?next=%2Fdashboard",
        },
      });
    });

    expect(screen.getByText("Google 로그인 페이지로 이동합니다.")).toBeInTheDocument();
  });

  it("disables the button while OAuth starts", async () => {
    let resolveSignIn: ((value: { error: null }) => void) | undefined;
    signInWithOAuth.mockImplementation(
      () =>
        new Promise((resolve) => {
          resolveSignIn = resolve;
        }),
    );
    const user = userEvent.setup();

    render(<LoginCard bodyClassName="body" />);

    const button = screen.getByRole("button", { name: "Continue with Google" });
    await user.click(button);

    expect(screen.getByRole("button", { name: "Google 연결 중..." })).toBeDisabled();

    resolveSignIn?.({ error: null });

    await waitFor(() => {
      expect(screen.getByRole("button", { name: "Continue with Google" })).not.toBeDisabled();
    });
  });

  it("shows a failure message when OAuth start fails", async () => {
    signInWithOAuth.mockResolvedValue({ error: new Error("boom") });
    const user = userEvent.setup();

    render(<LoginCard bodyClassName="body" />);

    await user.click(screen.getByRole("button", { name: "Continue with Google" }));

    expect(
      await screen.findByText("Google 로그인을 시작하지 못했습니다. 다시 시도하세요."),
    ).toBeInTheDocument();
  });

  it("renders callback failure messages from the page", () => {
    render(
      <LoginCard
        bodyClassName="body"
        errorMessage="로그인 처리에 실패했습니다. 다시 시도하세요."
      />,
    );

    expect(screen.getByText("로그인 처리에 실패했습니다. 다시 시도하세요.")).toBeInTheDocument();
  });
});
