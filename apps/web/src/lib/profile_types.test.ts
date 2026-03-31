import { describe, expect, it } from "vitest";

import {
  mapOnboardingFormStateToProfilePayload,
  mapProfileToOnboardingFormState,
  type UserProfileResponse,
} from "@/lib/profile_types";

describe("profile_types", () => {
  it("maps API profile data into onboarding form state", () => {
    const profile: UserProfileResponse = {
      user_id: "89b6698f-d88b-4b83-baa8-23a3a8ee7f92",
      email: "scaffold-user@example.com",
      profile_data: {
        role: "Machine Learning Engineer",
        years_of_experience: 6,
        title_keywords: ["machine learning engineer"],
      },
      guidelines: {
        must_haves: ["Python", "SQL"],
        deal_breakers: ["contract-only"],
      },
      preferences: {
        work_modes: [],
        locations: [],
        team_contexts: [],
        skills: { preset: [], custom: [] },
        exclusions: { preset: [], custom: [] },
        comparisons: {},
        note: null,
      },
      notification_settings: {
        minimum_fit_score: 82,
        delivery_channel: "slack",
      },
    };

    expect(mapProfileToOnboardingFormState(profile)).toEqual({
      role: "Machine Learning Engineer",
      yearsOfExperience: "6",
      mustHaves: "Python, SQL",
      dealBreakers: "contract-only",
      minimumFitScore: "82",
    });
  });

  it("maps onboarding form state into the profile update payload", () => {
    expect(
      mapOnboardingFormStateToProfilePayload({
        role: "Machine Learning Engineer",
        yearsOfExperience: "6",
        mustHaves: "Python, SQL, Python",
        dealBreakers: "contract-only, remote-only",
        minimumFitScore: "85",
      }),
    ).toEqual({
      profile_data: {
        role: "Machine Learning Engineer",
        years_of_experience: 6,
      },
      guidelines: {
        must_haves: ["Python", "SQL", "Python"],
        deal_breakers: ["contract-only", "remote-only"],
      },
      notification_settings: {
        minimum_fit_score: 85,
      },
    });
  });
});
