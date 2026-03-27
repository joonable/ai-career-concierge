import React from "react";

export default function DashboardLoading() {
  return (
    <main className="dashboard-page" aria-busy="true">
      <div className="dashboard-shell">
        <section className="dashboard-grid">
          <article className="dashboard-card dashboard-card--span-2 dashboard-loading-card">
            <span className="dashboard-kicker">Dashboard</span>
            <div className="dashboard-loading-copy">
              <div className="dashboard-skeleton dashboard-skeleton--title" />
              <div className="dashboard-skeleton dashboard-skeleton--body" />
            </div>
            <p className="dashboard-meta">대시보드를 불러오는 중입니다.</p>
          </article>
          <article className="dashboard-card dashboard-loading-card">
            <span className="dashboard-kicker">Profile</span>
            <div className="dashboard-loading-copy">
              <div className="dashboard-skeleton dashboard-skeleton--body" />
              <div className="dashboard-skeleton dashboard-skeleton--body" />
              <div className="dashboard-skeleton dashboard-skeleton--body" />
            </div>
          </article>
        </section>
        <section className="dashboard-board" aria-hidden="true">
          <div className="dashboard-section__header">
            <div>
              <span className="dashboard-kicker">Matches</span>
              <h2 className="dashboard-section__title">추천 목록</h2>
            </div>
          </div>
          <div className="dashboard-card-grid">
            <article className="dashboard-card dashboard-loading-card" />
            <article className="dashboard-card dashboard-loading-card" />
            <article className="dashboard-card dashboard-loading-card" />
          </div>
        </section>
      </div>
    </main>
  );
}
