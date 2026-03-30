import { describe, expect, it } from "vitest";

import { mapDashboardRecommendations } from "@/lib/dashboard_mapper";

describe("mapDashboardRecommendations", () => {
  it("maps API recommendations to dashboard card props", () => {
    const recommendations = mapDashboardRecommendations({
      user_id: "user-1",
      minimum_fit_score: 80,
      recommendations: [
        {
          evaluation_id: "eval-1",
          status: "LLM_EVALUATED",
          fit_score: 91,
          reasoning: "Strong backend and ML overlap.",
          rule_rejection_reason: null,
          user_feedback: "DISLIKE",
          feedback_reason: "Too much onsite time",
          created_at: "2026-03-30T00:00:00Z",
          updated_at: "2026-03-30T01:00:00Z",
          job_id: "job-1",
          title: "Senior Machine Learning Engineer",
          company: "Signal Labs",
          url: "https://example.com/jobs/1",
          platform: "LinkedIn",
          jd_raw_text: "Python SQL ML platform ownership.",
          min_years_experience: 5,
          max_years_experience: 8,
          source_metadata: { location: "Seoul" },
        },
      ],
    });

    expect(recommendations).toEqual([
      {
        evaluationId: "eval-1",
        status: "LLM_EVALUATED",
        statusLabel: "평가 완료",
        fitScore: 91,
        reasoning: "Strong backend and ML overlap.",
        ruleRejectionReason: null,
        userFeedback: "DISLIKE",
        feedbackLabel: "제외",
        feedbackReason: "Too much onsite time",
        createdAt: "2026-03-30T00:00:00Z",
        updatedAt: "2026-03-30T01:00:00Z",
        title: "Senior Machine Learning Engineer",
        company: "Signal Labs",
        url: "https://example.com/jobs/1",
        platform: "LinkedIn",
        jdRawText: "Python SQL ML platform ownership.",
        minYearsExperience: 5,
        maxYearsExperience: 8,
        sourceMetadata: { location: "Seoul" },
      },
    ]);
  });

  it("formats unknown status and feedback values into readable fallback labels", () => {
    const recommendations = mapDashboardRecommendations({
      user_id: "user-1",
      minimum_fit_score: 80,
      recommendations: [
        {
          evaluation_id: "eval-1",
          status: "CUSTOM_STATUS",
          fit_score: null,
          reasoning: null,
          rule_rejection_reason: "TITLE_MISMATCH",
          user_feedback: "CUSTOM_FEEDBACK",
          feedback_reason: null,
          created_at: "2026-03-30T00:00:00Z",
          updated_at: "2026-03-30T01:00:00Z",
          job_id: "job-1",
          title: "Role",
          company: "Company",
          url: "https://example.com/jobs/1",
          platform: "Wanted",
          jd_raw_text: "Contract-only onsite role.",
          min_years_experience: null,
          max_years_experience: null,
          source_metadata: {},
        },
      ],
    });

    expect(recommendations[0]?.statusLabel).toBe("Custom Status");
    expect(recommendations[0]?.feedbackLabel).toBe("Custom Feedback");
    expect(recommendations[0]?.fitScore).toBeNull();
    expect(recommendations[0]?.reasoning).toBeNull();
    expect(recommendations[0]?.ruleRejectionReason).toBe("TITLE_MISMATCH");
  });
});
