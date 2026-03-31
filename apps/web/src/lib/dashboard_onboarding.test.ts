import { describe, expect, it } from "vitest";

import { deriveDashboardOnboardingState } from "@/lib/dashboard_onboarding";
import type { UserProfileResponse } from "@/lib/profile_types";

function buildProfile(overrides?: Partial<UserProfileResponse>): UserProfileResponse {
  return {
    user_id: "89b6698f-d88b-4b83-baa8-23a3a8ee7f92",
    email: "scaffold-user@example.com",
    profile_data: {
      role: "",
      years_of_experience: 6,
      title_keywords: [],
      ...overrides?.profile_data,
    },
    guidelines: {
      must_haves: [],
      deal_breakers: [],
      ...overrides?.guidelines,
    },
    preferences: {
      work_modes: [],
      locations: [],
      team_contexts: [],
      skills: { preset: [], custom: [] },
      exclusions: { preset: [], custom: [] },
      comparisons: {},
      note: null,
      ...overrides?.preferences,
    },
    notification_settings: {
      minimum_fit_score: 82,
      delivery_channel: "slack",
      ...overrides?.notification_settings,
    },
  };
}

describe("dashboard_onboarding", () => {
  it("treats role-only profiles as incomplete and exposes missing fields", () => {
    const state = deriveDashboardOnboardingState(
      buildProfile({
        profile_data: {
          role: "ML Engineer",
          years_of_experience: 6,
          title_keywords: [],
        },
      }),
    );

    expect(state.isComplete).toBe(false);
    expect(state.completionLabel).toBe("1/3 입력");
    expect(state.missingFields).toEqual(["skills", "exclusions"]);
    expect(state.fields.map((field) => field.statusLabel)).toEqual(["입력됨", "미입력", "미입력"]);
  });

  it("marks onboarding complete once role, skills, and exclusions exist", () => {
    const state = deriveDashboardOnboardingState(
      buildProfile({
        profile_data: {
          role: "ML Engineer",
          years_of_experience: 6,
          title_keywords: [],
        },
        preferences: {
          work_modes: [],
          locations: [],
          team_contexts: [],
          skills: { preset: ["python", "llm"], custom: [] },
          exclusions: { preset: ["onsite-only"], custom: [] },
          comparisons: {},
          note: null,
        },
      }),
    );

    expect(state.isComplete).toBe(true);
    expect(state.completionLabel).toBe("3/3 입력");
    expect(state.missingFields).toEqual([]);
    expect(state.preferredSkills).toEqual(["Python", "LLM application"]);
    expect(state.exclusions).toEqual(["상주 출근만 가능"]);
  });
});
