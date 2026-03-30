import { describe, expect, it } from "vitest";

import { mapDashboardRecommendations } from "@/lib/dashboard_mapper";
import type { DashboardApiRecommendation } from "@/lib/dashboard_types";

function buildApiRecommendation(
  overrides: Partial<DashboardApiRecommendation> = {},
): DashboardApiRecommendation {
  return {
    evaluation_id: "eval-1",
    status: "LLM_EVALUATED",
    fit_score: 91,
    reasoning: "Strong backend and ML overlap.",
    decision_summary: "적합도 91점으로 추천 기준을 넘겼습니다.",
    match_highlights: ["필수 조건 일치: Python", "직무 키워드가 공고 제목과 일치합니다."],
    risk_highlights: ["주의 조건 감지: onsite-only"],
    confidence_level: "HIGH",
    rule_rejection_reason: null,
    rule_match_reasons: ["목표 직무와 공고 제목이 일치합니다."],
    rule_rejection_details: [],
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
    responsibilities: ["Serve production recommender systems"],
    requirements: ["Python experience", "SQL experience"],
    preferred_requirements: ["MLOps experience"],
    location: "Seoul",
    employment_type: "Full-time",
    ...overrides,
  };
}

describe("mapDashboardRecommendations", () => {
  it("maps API recommendations to dashboard card props", () => {
    const recommendations = mapDashboardRecommendations({
      user_id: "user-1",
      minimum_fit_score: 80,
      recommendations: [buildApiRecommendation()],
    });

    expect(recommendations).toEqual([
      {
        evaluationId: "eval-1",
        status: "LLM_EVALUATED",
        statusLabel: "평가 완료",
        fitScore: 91,
        reasoning: "Strong backend and ML overlap.",
        decisionSummary: "적합도 91점으로 추천 기준을 넘겼습니다.",
        matchHighlights: ["필수 조건 일치: Python", "직무 키워드가 공고 제목과 일치합니다."],
        riskHighlights: ["주의 조건 감지: onsite-only"],
        confidenceLevel: "HIGH",
        ruleRejectionReason: null,
        ruleMatchReasons: ["목표 직무와 공고 제목이 일치합니다."],
        ruleRejectionDetails: [],
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
        responsibilities: ["Serve production recommender systems"],
        requirements: ["Python experience", "SQL experience"],
        preferredRequirements: ["MLOps experience"],
        location: "Seoul",
        employmentType: "Full-time",
      },
    ]);
  });

  it("formats unknown status and feedback values into readable fallback labels", () => {
    const recommendations = mapDashboardRecommendations({
      user_id: "user-1",
      minimum_fit_score: 80,
      recommendations: [
        buildApiRecommendation({
          status: "CUSTOM_STATUS",
          fit_score: null,
          reasoning: null,
          decision_summary: null,
          match_highlights: [],
          risk_highlights: [],
          confidence_level: "LOW",
          rule_rejection_reason: "TITLE_MISMATCH",
          rule_match_reasons: [],
          rule_rejection_details: ["직무 키워드 불일치"],
          user_feedback: "CUSTOM_FEEDBACK",
          feedback_reason: null,
          title: "Role",
          company: "Company",
          platform: "Wanted",
          jd_raw_text: "Contract-only onsite role.",
          min_years_experience: null,
          max_years_experience: null,
          source_metadata: {},
          location: null,
          employment_type: null,
          responsibilities: [],
          requirements: [],
          preferred_requirements: [],
        }),
      ],
    });

    expect(recommendations[0]?.statusLabel).toBe("Custom Status");
    expect(recommendations[0]?.feedbackLabel).toBe("Custom Feedback");
    expect(recommendations[0]?.fitScore).toBeNull();
    expect(recommendations[0]?.reasoning).toBeNull();
    expect(recommendations[0]?.ruleRejectionReason).toBe("TITLE_MISMATCH");
  });
});
