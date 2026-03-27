import React from "react";
import type { DashboardRecommendation } from "@/lib/dashboard_mapper";

type RecommendationBoardProps = {
  minimumFitScore: number;
  recommendations: DashboardRecommendation[];
};

export function RecommendationBoard({
  minimumFitScore,
  recommendations,
}: RecommendationBoardProps) {
  return (
    <section className="dashboard-board">
      <div className="dashboard-section__header">
        <div>
          <span className="dashboard-kicker">Matches</span>
          <h2 className="dashboard-section__title">추천 목록</h2>
        </div>
        <p className="dashboard-meta">기준 {minimumFitScore}+</p>
      </div>
      <div className="dashboard-card-grid">
        {recommendations.length === 0 ? (
          <article className="dashboard-card dashboard-card--full dashboard-empty-state">
            <span className="dashboard-kicker">Queue</span>
            <h3 className="dashboard-empty-state__title">아직 비어 있습니다</h3>
            <p className="dashboard-meta">파이프라인 실행 후 여기에 표시됩니다.</p>
          </article>
        ) : (
          recommendations.map((recommendation) => (
            <article
              className="dashboard-card dashboard-card--interactive dashboard-recommendation"
              key={recommendation.evaluationId}
            >
              <div className="dashboard-recommendation__top">
                <div className="dashboard-score">
                  <strong>{recommendation.fitScore ?? "--"}</strong>
                  <span>{recommendation.fitScore === null ? "대기" : "적합도"}</span>
                </div>
                <span className="dashboard-pill">{recommendation.statusLabel}</span>
              </div>
              <div>
                <h3 className="dashboard-recommendation__title">{recommendation.title}</h3>
                <p className="dashboard-meta">
                  {recommendation.company} · {recommendation.platform}
                </p>
              </div>
              <p className="dashboard-recommendation__reasoning">
                {recommendation.reasoning ?? "정밀 평가 대기 중"}
              </p>
              <div className="dashboard-recommendation__footer">
                <div className="dashboard-chip-list">
                  <span className="dashboard-chip">{recommendation.platform}</span>
                  {recommendation.feedbackLabel ? (
                    <span className="dashboard-chip dashboard-chip--muted">
                      피드백 {recommendation.feedbackLabel}
                    </span>
                  ) : null}
                </div>
                <a
                  className="dashboard-link"
                  href={recommendation.url}
                  rel="noreferrer"
                  target="_blank"
                >
                  공고 보기
                </a>
              </div>
            </article>
          ))
        )}
      </div>
    </section>
  );
}
