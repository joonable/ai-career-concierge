import type { DashboardResponse } from "@/lib/dashboard_types";

export type DashboardRecommendation = {
  evaluationId: string;
  status: string;
  statusLabel: string;
  fitScore: number | null;
  reasoning: string | null;
  decisionSummary: string | null;
  matchHighlights: string[];
  riskHighlights: string[];
  confidenceLevel: string;
  ruleRejectionReason: string | null;
  ruleMatchReasons: string[];
  ruleRejectionDetails: string[];
  userFeedback: string | null;
  feedbackLabel: string | null;
  feedbackReason: string | null;
  createdAt: string;
  updatedAt: string;
  title: string;
  company: string;
  url: string;
  platform: string;
  jdRawText: string;
  minYearsExperience: number | null;
  maxYearsExperience: number | null;
  sourceMetadata: Record<string, unknown>;
  responsibilities: string[];
  requirements: string[];
  preferredRequirements: string[];
  location: string | null;
  employmentType: string | null;
};

export function mapDashboardRecommendations(
  dashboard: DashboardResponse,
): DashboardRecommendation[] {
  return dashboard.recommendations.map((recommendation) => ({
    evaluationId: recommendation.evaluation_id,
    status: recommendation.status,
    statusLabel: formatEvaluationStatus(recommendation.status),
    fitScore: recommendation.fit_score,
    reasoning: recommendation.reasoning,
    decisionSummary: recommendation.decision_summary,
    matchHighlights: recommendation.match_highlights,
    riskHighlights: recommendation.risk_highlights,
    confidenceLevel: recommendation.confidence_level,
    ruleRejectionReason: recommendation.rule_rejection_reason,
    ruleMatchReasons: recommendation.rule_match_reasons,
    ruleRejectionDetails: recommendation.rule_rejection_details,
    userFeedback: recommendation.user_feedback,
    feedbackLabel: formatFeedback(recommendation.user_feedback),
    feedbackReason: recommendation.feedback_reason,
    createdAt: recommendation.created_at,
    updatedAt: recommendation.updated_at,
    title: recommendation.title,
    company: recommendation.company,
    url: recommendation.url,
    platform: recommendation.platform,
    jdRawText: recommendation.jd_raw_text,
    minYearsExperience: recommendation.min_years_experience,
    maxYearsExperience: recommendation.max_years_experience,
    sourceMetadata: recommendation.source_metadata,
    responsibilities: recommendation.responsibilities,
    requirements: recommendation.requirements,
    preferredRequirements: recommendation.preferred_requirements,
    location: recommendation.location,
    employmentType: recommendation.employment_type,
  }));
}

function formatEvaluationStatus(status: string) {
  switch (status) {
    case "PENDING":
      return "대기";
    case "RULE_REJECTED":
      return "규칙 제외";
    case "LLM_EVALUATED":
      return "평가 완료";
    default:
      return formatFallbackLabel(status);
  }
}

function formatFeedback(feedback: string | null) {
  switch (feedback) {
    case "LIKE":
      return "좋아요";
    case "DISLIKE":
      return "제외";
    case "LATER":
      return "나중에 보기";
    default:
      return feedback ? formatFallbackLabel(feedback) : null;
  }
}

function formatFallbackLabel(value: string) {
  return value
    .toLowerCase()
    .split("_")
    .map((token) => token.charAt(0).toUpperCase() + token.slice(1))
    .join(" ");
}
