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

export function mapDashboardRecommendations(dashboard: DashboardResponse) {
  return dashboard.recommendations.map((recommendation) => ({
    evaluationId: recommendation.evaluation_id,
    status: recommendation.status,
    fitScore: recommendation.fit_score,
    reasoning: recommendation.reasoning,
    userFeedback: recommendation.user_feedback,
    feedbackReason: recommendation.feedback_reason,
    title: recommendation.title,
    company: recommendation.company,
    url: recommendation.url,
    platform: recommendation.platform,
  }));
}
