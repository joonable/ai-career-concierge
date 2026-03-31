import Link from "next/link";
import React from "react";

import { DashboardErrorState } from "@/components/dashboard/dashboard-error-state";
import { ensurePromptOpsAdminAccess } from "@/lib/promptops_access";
import { loadInternalPageData } from "@/lib/internal_loader";

const FALLBACK_VALUE = "아직 정리되지 않음";

export default async function InternalHomePage() {
  await ensurePromptOpsAdminAccess();

  const pageData = await loadInternalPageData();
  if (pageData.status === "error") {
    return (
      <main className="dashboard-page promptops-page">
        <div className="dashboard-shell">
          <DashboardErrorState message={pageData.message} />
        </div>
      </main>
    );
  }

  const { internalStatus, promptSummary } = pageData;

  return (
    <main className="dashboard-page promptops-page">
      <div className="dashboard-shell promptops-shell">
        <section className="dashboard-grid promptops-overview-grid">
          <article className="dashboard-card dashboard-card--active dashboard-card--span-2">
            <div className="dashboard-hero">
              <div className="dashboard-hero__top">
                <div className="dashboard-hero__copy">
                  <span className="dashboard-kicker">Internal</span>
                  <h1 className="dashboard-title">운영 허브</h1>
                  <p className="dashboard-subcopy">
                    현재 작업, milestone, 다음 액션, backlog를 한 화면에서 정리하고 Prompt 운영 패널로 바로 이어지는
                    내부 상황판입니다.
                  </p>
                </div>
                <span className="dashboard-pill dashboard-pill--accent">
                  {internalStatus.updatedAt || "문서 갱신 대기"}
                </span>
              </div>
              <div className="dashboard-stat-grid">
                <div className="dashboard-stat">
                  <span className="dashboard-stat__label">Current focus</span>
                  <strong>{internalStatus.currentFocus.length || 0}</strong>
                </div>
                <div className="dashboard-stat">
                  <span className="dashboard-stat__label">Open actions</span>
                  <strong>{internalStatus.actions.length || 0}</strong>
                </div>
                <div className="dashboard-stat">
                  <span className="dashboard-stat__label">Backlog items</span>
                  <strong>{internalStatus.backlog.length || 0}</strong>
                </div>
              </div>
            </div>
          </article>

          <Link className="dashboard-card dashboard-summary-card dashboard-card--interactive" href="/internal/prompts">
            <div className="dashboard-summary__header">
              <div className="dashboard-summary-card__copy">
                <span className="dashboard-kicker">Prompts</span>
                <h2 className="dashboard-section__title">프롬프트 운영 패널</h2>
              </div>
              <span className="dashboard-pill">{promptSummary.snapshot.prompt_family}</span>
            </div>
            <p className="dashboard-meta">
              최신 결정 {promptSummary.snapshot.latest_decision || FALLBACK_VALUE}
            </p>
            <ul className="promptops-list promptops-list--compact">
              {(promptSummary.docs.interpretation.length > 0
                ? promptSummary.docs.interpretation
                : promptSummary.snapshot.latest_summary
              )
                .slice(0, 2)
                .map((item) => (
                  <li key={item}>{item}</li>
                ))}
            </ul>
            <div className="dashboard-summary-card__footer">
              <span className="dashboard-summary-card__cta">PromptOps 작업대로 이동</span>
              <span className="dashboard-summary-card__arrow" aria-hidden="true">
                →
              </span>
            </div>
          </Link>
        </section>

        <section className="promptops-grid">
          <article className="dashboard-card promptops-card">
            <div className="dashboard-section__header">
              <div>
                <span className="dashboard-kicker">Current work</span>
                <h2 className="dashboard-section__title">현재 작업 중</h2>
              </div>
            </div>
            {internalStatus.currentFocus.length > 0 ? (
              <ul className="promptops-list">
                {internalStatus.currentFocus.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            ) : (
              <p className="promptops-empty">{FALLBACK_VALUE}</p>
            )}
          </article>

          <article className="dashboard-card promptops-card">
            <div className="dashboard-section__header">
              <div>
                <span className="dashboard-kicker">Milestone</span>
                <h2 className="dashboard-section__title">프로젝트 milestone 및 진행상황</h2>
              </div>
            </div>
            {internalStatus.milestones.length > 0 ? (
              <ul className="promptops-list">
                {internalStatus.milestones.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            ) : (
              <p className="promptops-empty">{FALLBACK_VALUE}</p>
            )}
          </article>
        </section>

        <section className="promptops-grid">
          <article className="dashboard-card promptops-card">
            <div className="dashboard-section__header">
              <div>
                <span className="dashboard-kicker">Action</span>
                <h2 className="dashboard-section__title">지금 해야 할 action</h2>
              </div>
            </div>
            {internalStatus.actions.length > 0 ? (
              <ul className="promptops-list">
                {internalStatus.actions.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            ) : (
              <p className="promptops-empty">{FALLBACK_VALUE}</p>
            )}
          </article>

          <article className="dashboard-card promptops-card">
            <div className="dashboard-section__header">
              <div>
                <span className="dashboard-kicker">Backlog</span>
                <h2 className="dashboard-section__title">앞으로의 backlog</h2>
              </div>
            </div>
            {internalStatus.backlog.length > 0 ? (
              <ul className="promptops-list">
                {internalStatus.backlog.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            ) : (
              <p className="promptops-empty">{FALLBACK_VALUE}</p>
            )}
          </article>
        </section>

        <section className="promptops-grid">
          <article className="dashboard-card promptops-card">
            <div className="dashboard-section__header">
              <div>
                <span className="dashboard-kicker">Notes</span>
                <h2 className="dashboard-section__title">운영 메모</h2>
              </div>
            </div>
            {internalStatus.notes.length > 0 ? (
              <ul className="promptops-list">
                {internalStatus.notes.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            ) : (
              <p className="promptops-empty">{FALLBACK_VALUE}</p>
            )}
          </article>

          <article className="dashboard-card promptops-card">
            <div className="dashboard-section__header">
              <div>
                <span className="dashboard-kicker">References</span>
                <h2 className="dashboard-section__title">참고 링크</h2>
              </div>
            </div>
            {internalStatus.references.length > 0 ? (
              <ul className="promptops-list promptops-list--links">
                {internalStatus.references.map((item) => (
                  <li key={item.url}>
                    <Link href={item.url} rel="noreferrer" target="_blank">
                      {item.label}
                    </Link>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="promptops-empty">{FALLBACK_VALUE}</p>
            )}
          </article>
        </section>
      </div>
    </main>
  );
}
