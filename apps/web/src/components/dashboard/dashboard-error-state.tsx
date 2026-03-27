import React from "react";

type DashboardErrorStateProps = {
  message: string;
};

export function DashboardErrorState({ message }: DashboardErrorStateProps) {
  return (
    <section className="dashboard-board" aria-live="polite">
      <div className="dashboard-section__header">
        <div>
          <span className="dashboard-kicker">Matches</span>
          <h2 className="dashboard-section__title">추천 목록</h2>
        </div>
      </div>
      <div className="dashboard-card-grid">
        <article className="dashboard-card dashboard-card--full dashboard-empty-state dashboard-empty-state--error">
          <span className="dashboard-kicker">Error</span>
          <h3 className="dashboard-empty-state__title">대시보드를 불러오지 못했습니다</h3>
          <p className="dashboard-meta onboarding-status--error">{message}</p>
        </article>
      </div>
    </section>
  );
}
