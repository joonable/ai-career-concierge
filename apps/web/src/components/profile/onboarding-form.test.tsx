import React from "react";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi, beforeEach } from "vitest";

import { OnboardingForm } from "@/components/profile/onboarding-form";

const updateProfile = vi.fn();

vi.mock("@/lib/api_client_browser", () => ({
  updateProfile: (...args: unknown[]) => updateProfile(...args),
}));

describe("OnboardingForm", () => {
  beforeEach(() => {
    updateProfile.mockReset();
  });

  it("surfaces backend error details when save fails", async () => {
    updateProfile.mockRejectedValue(new Error("Supabase data API request failed: blocked by CORS"));
    const user = userEvent.setup();

    render(
      <OnboardingForm
        initialProfile={{
          role: "ML Engineer",
          yearsOfExperience: "6",
          mustHaves: "Python",
          dealBreakers: "Onsite",
          minimumFitScore: "80",
        }}
      />,
    );

    await user.click(screen.getByRole("button", { name: "저장 후 대시보드로" }));

    expect(
      await screen.findByText("저장 실패: Supabase data API request failed: blocked by CORS"),
    ).toBeInTheDocument();
  });
});
