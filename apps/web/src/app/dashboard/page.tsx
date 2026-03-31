import Link from "next/link";
import React from "react";

import { DashboardErrorState } from "@/components/dashboard/dashboard-error-state";
import { OnboardingStatusCard } from "@/components/dashboard/onboarding-status-card";
import { RecommendationBoard } from "@/components/dashboard/recommendation-board";
import { loadDashboardPageData } from "@/lib/dashboard_loader";
import { mapDashboardRecommendations } from "@/lib/dashboard_mapper";
import { deriveDashboardOnboardingState } from "@/lib/dashboard_onboarding";
import { isPromptOpsAdminEmail } from "@/lib/promptops_access";

export default async function DashboardPage() {
  const dashboardPageData = await loadDashboardPageData();

  if (dashboardPageData.status === "error") {
    return (
      <main className="dashboard-page">
        <div className="dashboard-shell">
          <DashboardErrorState message={dashboardPageData.message} />
        </div>
      </main>
    );
  }

  const { dashboard, profile } = dashboardPageData;
  const recommendations = mapDashboardRecommendations(dashboard);
  const onboardingState = deriveDashboardOnboardingState(profile);
  const canAccessAdminPage = isPromptOpsAdminEmail(profile.email);

  return (
    <main className="dashboard-page">
      <div className="dashboard-shell">
        {canAccessAdminPage ? (
          <Link className="dashboard-admin-bar" href="/internal">
            <span className="dashboard-admin-bar__eyebrow">Admin</span>
            <strong>운영 허브로 이동</strong>
            <span className="dashboard-admin-bar__meta">milestone, action, PromptOps 작업대를 한 번에 확인합니다.</span>
          </Link>
        ) : null}
        <section className="dashboard-grid">
          <article className="dashboard-card dashboard-card--active dashboard-card--span-2">
            <div className="dashboard-hero">
              <div className="dashboard-hero__top">
                <div className="dashboard-hero__copy">
                  <span className="dashboard-kicker">Dashboard</span>
                  <h1 className="dashboard-title">추천 공고</h1>
                  <p className="dashboard-subcopy">
                    {onboardingState.isComplete
                      ? `${onboardingState.role} 기준으로 정리한 결과만 보여줍니다.`
                      : `추천 기준 ${onboardingState.completionLabel}. 남은 항목을 채우면 더 정확한 추천을 받을 수 있습니다.`}
                  </p>
                </div>
                <span className="dashboard-pill">
                  {profile.notification_settings.delivery_channel.toUpperCase()}
                </span>
              </div>
              <div className="dashboard-stat-grid">
                <div className="dashboard-stat">
                  <span className="dashboard-stat__label">추천 수</span>
                  <strong>{recommendations.length}</strong>
                </div>
                <div className="dashboard-stat">
                  <span className="dashboard-stat__label">최소 점수</span>
                  <strong>{dashboard.minimum_fit_score}+</strong>
                </div>
                <div className="dashboard-stat">
                  <span className="dashboard-stat__label">온보딩</span>
                  <strong>
                    {onboardingState.isComplete ? "완료" : onboardingState.completionLabel}
                  </strong>
                </div>
              </div>
            </div>
          </article>
          <OnboardingStatusCard state={onboardingState} />
        </section>
        <RecommendationBoard
          minimumFitScore={dashboard.minimum_fit_score}
          profile={profile}
          recommendations={recommendations}
        />
      </div>
    </main>
  );
}
