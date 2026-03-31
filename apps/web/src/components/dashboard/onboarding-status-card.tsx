import React from "react";
import Link from "next/link";

import type { DashboardOnboardingField, DashboardOnboardingState } from "@/lib/dashboard_onboarding";

type OnboardingStatusCardProps = {
  state: DashboardOnboardingState;
};

function renderCompactTags(items: string[]) {
  const visibleItems = items.slice(0, 3);
  const remainingCount = items.length - visibleItems.length;

  return (
    <>
      {visibleItems.map((item, index) => (
        <span className="dashboard-chip" key={`${item}-${index}`}>
          {item}
        </span>
      ))}
      {remainingCount > 0 ? (
        <span className="dashboard-chip dashboard-chip--muted">+{remainingCount}</span>
      ) : null}
    </>
  );
}

function ChecklistRow({ field }: { field: DashboardOnboardingField }) {
  return (
    <div
      className={[
        "dashboard-checklist__item",
        field.isComplete
          ? "dashboard-checklist__item--complete"
          : "dashboard-checklist__item--missing",
      ].join(" ")}
      role="listitem"
    >
      <span className="dashboard-checklist__status" aria-hidden="true">
        <span
          className={[
            "dashboard-checklist__dot",
            field.isComplete
              ? "dashboard-checklist__dot--complete"
              : "dashboard-checklist__dot--missing",
          ].join(" ")}
        />
      </span>
      <div className="dashboard-checklist__copy">
        <span className="dashboard-detail__label">{field.label}</span>
        <p className="dashboard-checklist__meta">{field.detail}</p>
      </div>
      <span
        className={[
          "dashboard-checklist__badge",
          field.isComplete
            ? "dashboard-checklist__badge--complete"
            : "dashboard-checklist__badge--missing",
        ].join(" ")}
      >
        {field.statusLabel}
      </span>
    </div>
  );
}

export function OnboardingStatusCard({ state }: OnboardingStatusCardProps) {
  const cardClassName = [
    "dashboard-card",
    "dashboard-card--interactive",
    "dashboard-summary-card",
    state.isComplete ? "dashboard-summary-card--complete" : "dashboard-summary-card--incomplete",
  ].join(" ");

  if (!state.isComplete) {
    return (
      <Link aria-label="온보딩 설정 열기" className={cardClassName} href="/onboarding">
        <div className="dashboard-summary__header">
          <div className="dashboard-summary-card__copy">
            <span className="dashboard-kicker">Profile</span>
            <h2 className="dashboard-section__title">추천 기준이 아직 부족합니다</h2>
          </div>
          <span className="dashboard-pill dashboard-pill--muted">{state.completionLabel}</span>
        </div>
        <p className="dashboard-meta">
          무엇이 비어 있는지 확인하고 바로 설정을 이어갈 수 있습니다.
        </p>
        <div className="dashboard-checklist" role="list">
          {state.fields.map((field) => (
            <ChecklistRow field={field} key={field.key} />
          ))}
        </div>
        <div className="dashboard-summary-card__footer">
          <span className="dashboard-summary-card__cta">온보딩 열기</span>
          <span aria-hidden="true" className="dashboard-summary-card__arrow">
            &gt;
          </span>
        </div>
      </Link>
    );
  }

  return (
    <Link aria-label="온보딩 설정 수정" className={cardClassName} href="/onboarding">
      <div className="dashboard-summary__header">
        <div className="dashboard-summary-card__copy">
          <span className="dashboard-kicker">Profile</span>
          <h2 className="dashboard-section__title">{state.role}</h2>
        </div>
        <span className="dashboard-pill dashboard-pill--accent">완료</span>
      </div>
      <p className="dashboard-meta">
        {state.yearsOfExperience}년 경력 · 최소 적합도 {state.minimumFitScore}+
      </p>
      <div className="dashboard-detail">
        <span className="dashboard-detail__label">중요 스킬</span>
        <div className="dashboard-chip-list">{renderCompactTags(state.preferredSkills)}</div>
      </div>
      <div className="dashboard-detail">
        <span className="dashboard-detail__label">제외 조건</span>
        <div className="dashboard-chip-list">{renderCompactTags(state.exclusions)}</div>
      </div>
      <div className="dashboard-summary-card__footer">
        <span className="dashboard-summary-card__cta dashboard-summary-card__cta--subtle">
          설정 보기
        </span>
        <span aria-hidden="true" className="dashboard-summary-card__arrow">
          &gt;
        </span>
      </div>
    </Link>
  );
}
