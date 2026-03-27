import React from "react";

import { OnboardingForm } from "@/components/profile/onboarding-form";
import { getProfileSnapshot } from "@/lib/api_client_server";
import {
  EMPTY_ONBOARDING_FORM_STATE,
  mapProfileToOnboardingFormState,
} from "@/lib/profile_types";

function buildRequiredItems(initialProfile: typeof EMPTY_ONBOARDING_FORM_STATE) {
  return [
    {
      label: "목표 직무",
      isComplete: initialProfile.role.trim().length > 0,
    },
    {
      label: "필수 조건",
      isComplete: initialProfile.mustHaves.trim().length > 0,
    },
    {
      label: "비선호 조건",
      isComplete: initialProfile.dealBreakers.trim().length > 0,
    },
  ];
}

export default async function OnboardingPage() {
  let initialProfile = EMPTY_ONBOARDING_FORM_STATE;

  try {
    const profile = await getProfileSnapshot();
    initialProfile = mapProfileToOnboardingFormState(profile);
  } catch {
    initialProfile = EMPTY_ONBOARDING_FORM_STATE;
  }

  const requiredItems = buildRequiredItems(initialProfile);
  const completedCount = requiredItems.filter((item) => item.isComplete).length;

  return (
    <main className="dashboard-page onboarding-page">
      <div className="dashboard-shell">
        <section className="dashboard-grid onboarding-page__grid">
          <article className="dashboard-card dashboard-card--active dashboard-card--span-2 onboarding-hero-card">
            <div className="dashboard-hero">
              <div className="dashboard-hero__copy">
                <span className="dashboard-kicker">Onboarding</span>
                <h1 className="dashboard-title onboarding-page__title">추천 기준을 먼저 맞춥니다</h1>
                <p className="dashboard-subcopy">
                  여기서 저장한 값은 프로필, 가이드라인, 최소 적합도 기준으로 바로 반영됩니다.
                </p>
              </div>
              <div className="dashboard-chip-list">
                <span className="dashboard-chip">목표 직무</span>
                <span className="dashboard-chip">필수 조건</span>
                <span className="dashboard-chip">비선호 조건</span>
                <span className="dashboard-chip dashboard-chip--muted">
                  최소 적합도 {initialProfile.minimumFitScore || "80"}
                </span>
              </div>
            </div>
          </article>
          <article className="dashboard-card onboarding-page__summary">
            <div className="dashboard-summary__header">
              <div className="dashboard-summary-card__copy">
                <span className="dashboard-kicker">Required</span>
                <h2 className="dashboard-section__title">핵심 3개 항목</h2>
              </div>
              <span
                className={
                  completedCount === requiredItems.length
                    ? "dashboard-pill dashboard-pill--accent"
                    : "dashboard-pill dashboard-pill--muted"
                }
              >
                {completedCount}/{requiredItems.length} 입력
              </span>
            </div>
            <div className="dashboard-checklist" role="list">
              {requiredItems.map((item) => (
                <div
                  className={[
                    "dashboard-checklist__item",
                    item.isComplete
                      ? "dashboard-checklist__item--complete"
                      : "dashboard-checklist__item--missing",
                  ].join(" ")}
                  key={item.label}
                  role="listitem"
                >
                  <span className="dashboard-checklist__status" aria-hidden="true">
                    <span
                      className={[
                        "dashboard-checklist__dot",
                        item.isComplete
                          ? "dashboard-checklist__dot--complete"
                          : "dashboard-checklist__dot--missing",
                      ].join(" ")}
                    />
                  </span>
                  <div className="dashboard-checklist__copy">
                    <span className="dashboard-detail__label">{item.label}</span>
                    <p className="dashboard-checklist__meta">
                      {item.isComplete ? "입력됨" : "아직 비어 있음"}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </article>
        </section>
        <OnboardingForm initialProfile={initialProfile} />
      </div>
    </main>
  );
}
