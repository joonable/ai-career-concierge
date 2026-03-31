import { describe, expect, it } from "vitest";

import {
  EMPTY_PREFERENCES,
  EMPTY_USER_PROFILE_RESPONSE,
  type UserProfileResponse,
} from "@/lib/profile_types";

describe("profile_types", () => {
  it("provides a stable empty profile response shape for onboarding fallbacks", () => {
    expect(EMPTY_USER_PROFILE_RESPONSE.profile_data.role).toBe("");
    expect(EMPTY_USER_PROFILE_RESPONSE.preferences).toEqual(EMPTY_PREFERENCES);
    expect(EMPTY_USER_PROFILE_RESPONSE.notification_settings.minimum_fit_score).toBe(80);
  });

  it("supports structured preference fields on profile responses", () => {
    const profile: UserProfileResponse = {
      user_id: "89b6698f-d88b-4b83-baa8-23a3a8ee7f92",
      email: "scaffold-user@example.com",
      profile_data: {
        role: "ML Engineer",
        roles: ["ml-engineer", "llm-engineer"],
        primary_role: "ml-engineer",
        years_of_experience: 6,
        seniority: "senior",
        title_keywords: ["ml engineer", "llm engineer"],
      },
      guidelines: {
        must_haves: ["python", "rag"],
        deal_breakers: ["contract"],
      },
      preferences: {
        work_modes: ["hybrid"],
        locations: ["seoul"],
        team_contexts: ["ai-first"],
        skills: { preset: ["python", "rag"], custom: ["Spark"] },
        exclusions: { preset: ["contract"], custom: ["박사 학위 필수"] },
        comparisons: { "delivery-vs-research": 1 },
        note: "B2B SaaS 선호",
      },
      notification_settings: {
        minimum_fit_score: 82,
        delivery_channel: "slack",
      },
    };

    expect(profile.preferences.skills.preset).toEqual(["python", "rag"]);
    expect(profile.profile_data.primary_role).toBe("ml-engineer");
    expect(profile.notification_settings.minimum_fit_score).toBe(82);
  });
});
