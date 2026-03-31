import React from "react";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { OnboardingForm } from "@/components/profile/onboarding-form";
import type { UserProfileResponse } from "@/lib/profile_types";

const updateProfile = vi.fn();

vi.mock("@/lib/api_client_browser", () => ({
  updateProfile: (...args: unknown[]) => updateProfile(...args),
}));

function buildProfile(overrides?: Partial<UserProfileResponse>): UserProfileResponse {
  return {
    user_id: "user-1",
    email: "scaffold-user@example.com",
    profile_data: {
      role: "ML Engineer",
      roles: ["ml-engineer"],
      primary_role: "ml-engineer",
      years_of_experience: 6,
      seniority: "senior",
      title_keywords: ["ml engineer"],
    },
    preferences: {
      work_modes: ["hybrid"],
      locations: ["seoul"],
      team_contexts: ["ai-first"],
      skills: { preset: ["python"], custom: ["Spark"] },
      exclusions: { preset: ["contract"], custom: ["박사 학위 필수"] },
      comparisons: { "delivery-vs-research": 1 },
      note: "B2B SaaS 선호",
    },
    guidelines: {
      must_haves: ["python", "Spark"],
      deal_breakers: ["contract", "박사 학위 필수"],
    },
    notification_settings: {
      minimum_fit_score: 80,
      delivery_channel: "slack",
    },
    ...overrides,
  };
}

describe("OnboardingForm", () => {
  beforeEach(() => {
    updateProfile.mockReset();
  });

  it("restores structured preferences into the form summary", () => {
    render(<OnboardingForm initialProfile={buildProfile()} />);

    expect(screen.getAllByText("ML Engineer").length).toBeGreaterThan(0);
    expect(screen.getAllByText("시니어").length).toBeGreaterThan(0);
    expect(screen.getAllByText("하이브리드").length).toBeGreaterThan(0);
    expect(screen.getAllByText("서울").length).toBeGreaterThan(0);
    expect(screen.getAllByText("Spark").length).toBeGreaterThan(0);
    expect(screen.getAllByText("박사 학위 필수").length).toBeGreaterThan(0);
  });

  it("submits the structured payload shape", async () => {
    updateProfile.mockResolvedValue(buildProfile());
    const user = userEvent.setup();

    render(<OnboardingForm initialProfile={buildProfile()} />);

    await user.click(screen.getByRole("button", { name: "저장 후 대시보드로" }));

    expect(updateProfile).toHaveBeenCalledWith({
      profile_data: {
        role: "ML Engineer",
        roles: ["ml-engineer"],
        primary_role: "ml-engineer",
        years_of_experience: 7,
        seniority: "senior",
        title_keywords: ["ml engineer"],
      },
      preferences: {
        work_modes: ["hybrid"],
        locations: ["seoul"],
        team_contexts: ["ai-first"],
        skills: { preset: ["python"], custom: ["Spark"] },
        exclusions: { preset: ["contract"], custom: ["박사 학위 필수"] },
        comparisons: { "delivery-vs-research": 1 },
        note: "B2B SaaS 선호",
      },
      notification_settings: {
        minimum_fit_score: 80,
      },
    });
  });

  it("surfaces backend error details when save fails", async () => {
    updateProfile.mockRejectedValue(new Error("Supabase data API request failed: blocked by CORS"));
    const user = userEvent.setup();

    render(<OnboardingForm initialProfile={buildProfile()} />);

    await user.click(screen.getByRole("button", { name: "저장 후 대시보드로" }));

    expect(
      await screen.findByText("저장 실패: Supabase data API request failed: blocked by CORS"),
    ).toBeInTheDocument();
  });
});
