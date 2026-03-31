import Link from "next/link";
import React from "react";

import { DashboardErrorState } from "@/components/dashboard/dashboard-error-state";
import { ensurePromptOpsAdminAccess } from "@/lib/promptops_access";
import { loadPromptOpsPageData } from "@/lib/promptops_loader";

export default async function PromptOpsIterationDetailPage() {
  await ensurePromptOpsAdminAccess();

  const pageData = await loadPromptOpsPageData();
  if (pageData.status === "error") {
    return (
      <main className="promptops-page">
        <div className="dashboard-shell">
          <DashboardErrorState message={pageData.message} />
        </div>
      </main>
    );
  }

  const { snapshot } = pageData;

  return (
    <main className="promptops-page">
      <div className="dashboard-shell promptops-shell">
        <section className="promptops-hero dashboard-card dashboard-card--active">
          <div className="promptops-hero__copy">
            <span className="dashboard-kicker">Iteration</span>
            <h1 className="dashboard-title">{snapshot.latest_iteration_title}</h1>
            <p className="dashboard-subcopy">
              현재 candidate 유지 결정에 영향을 준 핵심 실험 요약과 follow-up backlog를 보여줍니다.
            </p>
          </div>
          <Link className="promptops-inline-link" href="/internal/promptops">
            PromptOps 패널로 돌아가기
          </Link>
        </section>

        <section className="promptops-grid">
          <article className="dashboard-card promptops-card">
            <div className="promptops-card__header">
              <span className="dashboard-kicker">Decision</span>
              <h2>현재 판단</h2>
            </div>
            <p className="promptops-decision-detail">{snapshot.latest_decision}</p>
            <div className="promptops-link-list">
              <Link href={snapshot.compare_url} target="_blank" rel="noreferrer">
                LangSmith Compare 열기
              </Link>
              <Link href={snapshot.review_queue_url} target="_blank" rel="noreferrer">
                Review Queue 열기
              </Link>
            </div>
          </article>

          <article className="dashboard-card promptops-card">
            <div className="promptops-card__header">
              <span className="dashboard-kicker">Summary</span>
              <h2>핵심 변화</h2>
            </div>
            <ul className="promptops-list">
              {snapshot.latest_summary.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          </article>
        </section>

        <section className="dashboard-card promptops-card">
          <div className="promptops-card__header">
            <span className="dashboard-kicker">Backlog</span>
            <h2>다음 작업 후보</h2>
          </div>
          <ul className="promptops-list promptops-list--links">
            {snapshot.next_backlog_items.map((item) => (
              <li key={item.url}>
                <Link href={item.url} target="_blank" rel="noreferrer">
                  {item.title}
                </Link>
              </li>
            ))}
          </ul>
        </section>
      </div>
    </main>
  );
}
