import Link from "next/link";
import React from "react";

import { DashboardErrorState } from "@/components/dashboard/dashboard-error-state";
import { ensurePromptOpsAdminAccess } from "@/lib/promptops_access";
import { loadPromptOpsPageData } from "@/lib/promptops_loader";

const FALLBACK_VALUE = "아직 정리되지 않음";

export default async function PromptOpsPage() {
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
            <span className="dashboard-kicker">PromptOps</span>
            <h1 className="dashboard-title">운영 패널</h1>
            <p className="dashboard-subcopy">
              LangSmith, Notion, iteration 기록을 한 화면에서 확인하는 내부 전용 상태판입니다.
            </p>
          </div>
          <div className="promptops-decision">
            <span className="promptops-decision__label">Latest decision</span>
            <strong>{snapshot.latest_decision || FALLBACK_VALUE}</strong>
          </div>
        </section>

        <section className="promptops-grid">
          <article className="dashboard-card promptops-card">
            <div className="promptops-card__header">
              <span className="dashboard-kicker">현재 상태</span>
              <h2>Prompt lineage</h2>
            </div>
            <dl className="promptops-kv">
              <div>
                <dt>Production</dt>
                <dd>{snapshot.production_identifier || FALLBACK_VALUE}</dd>
              </div>
              <div>
                <dt>Staging</dt>
                <dd>{snapshot.staging_identifier || FALLBACK_VALUE}</dd>
              </div>
              <div>
                <dt>Candidate</dt>
                <dd>{snapshot.candidate_identifier || FALLBACK_VALUE}</dd>
              </div>
            </dl>
          </article>

          <article className="dashboard-card promptops-card">
            <div className="promptops-card__header">
              <span className="dashboard-kicker">핵심 링크</span>
              <h2>바로 이동</h2>
            </div>
            <div className="promptops-link-list">
              <Link href={snapshot.compare_url} target="_blank" rel="noreferrer">
                LangSmith Compare
              </Link>
              <Link href={snapshot.review_queue_url} target="_blank" rel="noreferrer">
                Review Queue ({snapshot.review_queue_name || FALLBACK_VALUE})
              </Link>
              <Link href={snapshot.notion_backlog_url} target="_blank" rel="noreferrer">
                Notion Backlog
              </Link>
              <Link href={snapshot.latest_iteration_url}>{snapshot.latest_iteration_title}</Link>
            </div>
          </article>
        </section>

        <section className="promptops-grid">
          <article className="dashboard-card promptops-card">
            <div className="promptops-card__header">
              <span className="dashboard-kicker">최근 요약</span>
              <h2>실험 해석</h2>
            </div>
            {snapshot.latest_summary.length > 0 ? (
              <ul className="promptops-list">
                {snapshot.latest_summary.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            ) : (
              <p className="promptops-empty">{FALLBACK_VALUE}</p>
            )}
          </article>

          <article className="dashboard-card promptops-card">
            <div className="promptops-card__header">
              <span className="dashboard-kicker">다음 backlog</span>
              <h2>Top 3</h2>
            </div>
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
              <p className="promptops-empty">{FALLBACK_VALUE}</p>
            )}
          </article>
        </section>
      </div>
    </main>
  );
}
