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
  const lineageItems = [
    { label: "Production", value: snapshot.production_identifier || FALLBACK_VALUE },
    { label: "Staging", value: snapshot.staging_identifier || FALLBACK_VALUE },
    { label: "Candidate", value: snapshot.candidate_identifier || FALLBACK_VALUE },
  ];
  const actionLinks = [
    {
      href: snapshot.compare_url,
      title: "Compare 실험 보기",
      description: "현재 candidate와 기준 프롬프트 차이를 바로 확인합니다.",
      external: true,
    },
    {
      href: snapshot.review_queue_url,
      title: `Review Queue ${snapshot.review_queue_name || FALLBACK_VALUE}`,
      description: "수동 검토가 필요한 케이스를 이어서 확인합니다.",
      external: true,
    },
    {
      href: snapshot.notion_backlog_url,
      title: "Notion Backlog 열기",
      description: "후속 작업 후보와 우선순위를 확인합니다.",
      external: true,
    },
    {
      href: snapshot.latest_iteration_url,
      title: snapshot.latest_iteration_title || "Latest iteration 보기",
      description: "가장 최근 iteration의 결정 배경을 살펴봅니다.",
      external: false,
    },
  ];

  return (
    <main className="dashboard-page promptops-page">
      <div className="dashboard-shell promptops-shell">
        <section className="dashboard-grid promptops-overview-grid">
          <article className="dashboard-card dashboard-card--active dashboard-card--span-2">
            <div className="dashboard-hero">
              <div className="dashboard-hero__top">
                <div className="dashboard-hero__copy">
                  <span className="dashboard-kicker">PromptOps</span>
                  <h1 className="dashboard-title">운영 패널</h1>
                  <p className="dashboard-subcopy">
                    LangSmith, Notion, iteration 기록을 한 화면에서 확인하고 다음 액션까지 바로 이어지는 내부 운영
                    상태판입니다.
                  </p>
                </div>
                <span className="dashboard-pill dashboard-pill--accent">Internal only</span>
              </div>
              <div className="dashboard-stat-grid">
                <div className="dashboard-stat">
                  <span className="dashboard-stat__label">Current decision</span>
                  <strong>{snapshot.latest_decision || FALLBACK_VALUE}</strong>
                </div>
                <div className="dashboard-stat">
                  <span className="dashboard-stat__label">Prompt family</span>
                  <strong>{snapshot.prompt_family || FALLBACK_VALUE}</strong>
                </div>
                <div className="dashboard-stat">
                  <span className="dashboard-stat__label">Next review</span>
                  <strong>{snapshot.review_queue_name || FALLBACK_VALUE}</strong>
                </div>
              </div>
            </div>
          </article>

          <article className="dashboard-card promptops-card">
            <div className="dashboard-summary__header">
              <div className="dashboard-summary-card__copy">
                <span className="dashboard-kicker">Current status</span>
                <h2 className="dashboard-section__title">Prompt lineage</h2>
              </div>
              <span className="dashboard-pill">{lineageItems.length} tracks</span>
            </div>
            <div className="promptops-lineage-grid">
              {lineageItems.map((item) => (
                <div className="promptops-lineage-item" key={item.label}>
                  <span className="promptops-lineage-item__label">{item.label}</span>
                  <strong>{item.value}</strong>
                </div>
              ))}
            </div>
          </article>
        </section>

        <section className="dashboard-card promptops-card dashboard-card--full">
          <div className="dashboard-section__header">
            <div>
              <span className="dashboard-kicker">Action</span>
              <h2 className="dashboard-section__title">바로 해야 할 일</h2>
            </div>
          </div>
          <div className="promptops-action-grid">
            {actionLinks.map((item) => (
              <Link
                className="promptops-action-card"
                href={item.href}
                key={item.title}
                rel={item.external ? "noreferrer" : undefined}
                target={item.external ? "_blank" : undefined}
              >
                <span className="promptops-action-card__eyebrow">Open</span>
                <strong>{item.title}</strong>
                <p>{item.description}</p>
              </Link>
            ))}
          </div>
        </section>

        <section className="promptops-grid">
          <article className="dashboard-card promptops-card">
            <div className="dashboard-section__header">
              <div>
                <span className="dashboard-kicker">Recent summary</span>
                <h2 className="dashboard-section__title">실험 해석</h2>
              </div>
            </div>
            <p className="dashboard-meta">가장 최근 iteration에서 남긴 판단 근거를 빠르게 읽을 수 있게 정리했습니다.</p>
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
            <div className="dashboard-section__header">
              <div>
                <span className="dashboard-kicker">Next backlog</span>
                <h2 className="dashboard-section__title">다음 작업 후보</h2>
              </div>
            </div>
            <p className="dashboard-meta">후속 iteration이나 기준 보정으로 바로 이어질 항목만 모아 보여줍니다.</p>
            {snapshot.next_backlog_items.length > 0 ? (
              <ul className="promptops-list promptops-list--links" aria-label="다음 작업 후보 목록">
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
