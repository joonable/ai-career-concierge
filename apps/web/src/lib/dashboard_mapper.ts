type DashboardResponse = {
  recommendations: Array<{
    evaluation_id: string;
    status: string;
    fit_score: number | null;
    reasoning: string | null;
    user_feedback: string | null;
    feedback_reason: string | null;
    title: string;
    company: string;
    url: string;
    platform: string;
  }>;
};

export type DashboardRecommendation = {
  evaluationId: string;
  status: string;
  statusLabel: string;
  fitScore: number | null;
  reasoning: string | null;
  userFeedback: string | null;
  feedbackLabel: string | null;
  feedbackReason: string | null;
  title: string;
  company: string;
  url: string;
  platform: string;
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
    userFeedback: recommendation.user_feedback,
    feedbackLabel: formatFeedback(recommendation.user_feedback),
    feedbackReason: recommendation.feedback_reason,
    title: recommendation.title,
    company: recommendation.company,
    url: recommendation.url,
    platform: recommendation.platform,
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
