import React from "react";

import { OnboardingForm } from "@/components/profile/onboarding-form";
import { getProfileSnapshot } from "@/lib/api_client_server";
import { EMPTY_USER_PROFILE_RESPONSE } from "@/lib/profile_types";

export default async function OnboardingPage() {
  let initialProfile = EMPTY_USER_PROFILE_RESPONSE;

  try {
    initialProfile = await getProfileSnapshot();
  } catch {
    initialProfile = EMPTY_USER_PROFILE_RESPONSE;
  }

  return (
    <main className="dashboard-page onboarding-page">
      <div className="dashboard-shell">
        <section className="dashboard-grid onboarding-page__grid onboarding-mockup__hero-grid">
          <article className="dashboard-card dashboard-card--active dashboard-card--span-3 onboarding-hero-card">
            <div className="dashboard-hero">
              <div className="dashboard-hero__copy">
                <span className="dashboard-kicker">Onboarding</span>
                <h1 className="dashboard-title onboarding-page__title">원하는 공고 기준을 빠르게 맞춰보세요</h1>
                <p className="dashboard-subcopy">
                  길게 설명하지 않아도 괜찮습니다. 선택한 기준은 다음 추천부터 바로 반영됩니다.
                </p>
              </div>
              <div className="dashboard-chip-list">
                <span className="dashboard-chip">직무</span>
                <span className="dashboard-chip">경력</span>
                <span className="dashboard-chip">스킬</span>
                <span className="dashboard-chip">제외 조건</span>
                <span className="dashboard-chip dashboard-chip--muted">
                  최소 적합도 {initialProfile.notification_settings.minimum_fit_score || 80}
                </span>
              </div>
            </div>
          </article>
        </section>
        <OnboardingForm initialProfile={initialProfile} />
      </div>
    </main>
  );
}
