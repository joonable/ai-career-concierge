import Link from "next/link";
import React from "react";

import { DashboardErrorState } from "@/components/dashboard/dashboard-error-state";
import { ensurePromptOpsAdminAccess } from "@/lib/promptops_access";
import { loadPromptOpsWorkspaceData } from "@/lib/internal_loader";

export default async function PromptOpsIterationDetailPage() {
  await ensurePromptOpsAdminAccess();

  const pageData = await loadPromptOpsWorkspaceData();
  if (pageData.status === "error") {
    return (
      <main className="dashboard-page promptops-page">
        <div className="dashboard-shell">
          <DashboardErrorState message={pageData.message} />
        </div>
      </main>
    );
  }

  const { snapshot } = pageData;

  return (
    <main className="dashboard-page promptops-page">
      <div className="dashboard-shell promptops-shell">
        <section className="dashboard-grid promptops-overview-grid">
          <article className="dashboard-card dashboard-card--active dashboard-card--span-2">
            <div className="dashboard-hero">
              <div className="dashboard-hero__top">
                <div className="dashboard-hero__copy">
                  <span className="dashboard-kicker">Iteration</span>
                  <h1 className="dashboard-title">{snapshot.latest_iteration_title}</h1>
                  <p className="dashboard-subcopy">
                    현재 candidate 유지 결정에 영향을 준 핵심 실험 요약과 follow-up backlog를 기존 운영 화면 리듬에 맞춰
                    보여줍니다.
                  </p>
                </div>
                <Link className="promptops-back-link" href="/internal/prompts">
                  프롬프트 운영 패널로 돌아가기
                </Link>
              </div>
              <div className="dashboard-stat-grid">
                <div className="dashboard-stat">
                  <span className="dashboard-stat__label">Current decision</span>
                  <strong>{snapshot.latest_decision}</strong>
                </div>
                <div className="dashboard-stat">
                  <span className="dashboard-stat__label">Review queue</span>
                  <strong>{snapshot.review_queue_name}</strong>
                </div>
                <div className="dashboard-stat">
                  <span className="dashboard-stat__label">Summary items</span>
                  <strong>{snapshot.latest_summary.length}</strong>
                </div>
              </div>
            </div>
          </article>

          <article className="dashboard-card promptops-card">
            <div className="dashboard-summary__header">
              <div className="dashboard-summary-card__copy">
                <span className="dashboard-kicker">Action</span>
                <h2 className="dashboard-section__title">바로 열기</h2>
              </div>
            </div>
            <div className="promptops-action-stack">
              <Link className="promptops-inline-link" href={snapshot.compare_url} target="_blank" rel="noreferrer">
                LangSmith Compare 열기
              </Link>
              <Link
                className="promptops-inline-link"
                href={snapshot.review_queue_url}
                target="_blank"
                rel="noreferrer"
              >
                Review Queue 열기
              </Link>
            </div>
          </article>
        </section>

        <section className="promptops-grid">
          <article className="dashboard-card promptops-card">
            <div className="dashboard-section__header">
              <div>
                <span className="dashboard-kicker">Decision</span>
                <h2 className="dashboard-section__title">현재 판단</h2>
              </div>
            </div>
            <p className="promptops-decision-detail">{snapshot.latest_decision}</p>
            <p className="dashboard-meta">
              최신 평가 방향을 유지할지, 수정할지 결정할 때 참고하는 현재 기준 요약입니다.
            </p>
          </article>

          <article className="dashboard-card promptops-card">
            <div className="dashboard-section__header">
              <div>
                <span className="dashboard-kicker">Summary</span>
                <h2 className="dashboard-section__title">핵심 변화</h2>
              </div>
            </div>
            <p className="dashboard-meta">이번 iteration에서 실제로 바뀐 해석 포인트를 빠르게 확인할 수 있습니다.</p>
            {snapshot.latest_summary.length > 0 ? (
              <ul className="promptops-list">
                {snapshot.latest_summary.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            ) : (
              <p className="promptops-empty">아직 정리되지 않음</p>
            )}
          </article>
        </section>

        <section className="dashboard-card promptops-card">
          <div className="dashboard-section__header">
            <div>
              <span className="dashboard-kicker">Backlog</span>
              <h2 className="dashboard-section__title">다음 작업 후보</h2>
            </div>
          </div>
          <p className="dashboard-meta">다음 실험이나 기준 보정으로 자연스럽게 이어질 후보를 정리했습니다.</p>
          {snapshot.next_backlog_items.length > 0 ? (
            <ul className="promptops-list promptops-list--links">
              {snapshot.next_backlog_items.map((item) => (
                <li key={item.url}>
                  <Link href={item.url} target="_blank" rel="noreferrer">
                    {item.title}
                  </Link>
                </li>
              ))}
            </ul>
          ) : (
            <p className="promptops-empty">아직 정리되지 않음</p>
          )}
        </section>
      </div>
    </main>
  );
}
