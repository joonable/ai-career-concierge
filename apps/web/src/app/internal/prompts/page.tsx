import Link from "next/link";
import React from "react";

import { DashboardErrorState } from "@/components/dashboard/dashboard-error-state";
import { loadPromptOpsWorkspaceData } from "@/lib/internal_loader";
import { ensurePromptOpsAdminAccess } from "@/lib/promptops_access";

const FALLBACK_VALUE = "아직 정리되지 않음";

export default async function InternalPromptsPage() {
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

  const { docs, snapshot } = pageData;
  const lineageItems = [
    { label: "Production", value: snapshot.production_identifier || FALLBACK_VALUE },
    { label: "Staging", value: snapshot.staging_identifier || FALLBACK_VALUE },
    { label: "Candidate", value: snapshot.candidate_identifier || FALLBACK_VALUE },
  ];
  const actionLinks = [
    {
      href: snapshot.compare_url,
      title: "Compare 실험 보기",
      description: "baseline과 candidate 차이를 바로 확인합니다.",
      external: true,
    },
    {
      href: snapshot.review_queue_url,
      title: `Review Queue ${snapshot.review_queue_name || FALLBACK_VALUE}`,
      description: "수동 검토가 필요한 queue를 이어서 봅니다.",
      external: true,
    },
    {
      href: snapshot.notion_backlog_url,
      title: "Notion Backlog 열기",
      description: "현재 prompt 후속 작업의 canonical backlog를 확인합니다.",
      external: true,
    },
    {
      href: snapshot.latest_iteration_url,
      title: snapshot.latest_iteration_title || "Latest iteration 보기",
      description: "가장 최근 반복 개선 기록을 읽습니다.",
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
                  <span className="dashboard-kicker">Prompt workspace</span>
                  <h1 className="dashboard-title">프롬프트 운영 패널</h1>
                  <p className="dashboard-subcopy">
                    lineage, 최신 결정, compare/review 링크, iteration 기록을 묶어서 관리하는 PromptOps 전용 작업대입니다.
                  </p>
                </div>
                <Link className="promptops-back-link" href="/internal">
                  운영 허브로 돌아가기
                </Link>
              </div>
              <div className="dashboard-stat-grid">
                <div className="dashboard-stat">
                  <span className="dashboard-stat__label">Prompt family</span>
                  <strong>{snapshot.prompt_family || FALLBACK_VALUE}</strong>
                </div>
                <div className="dashboard-stat">
                  <span className="dashboard-stat__label">Latest decision</span>
                  <strong>{snapshot.latest_decision || FALLBACK_VALUE}</strong>
                </div>
                <div className="dashboard-stat">
                  <span className="dashboard-stat__label">Docs updated</span>
                  <strong>{docs.updatedAt || FALLBACK_VALUE}</strong>
                </div>
              </div>
            </div>
          </article>

          <article className="dashboard-card promptops-card">
            <div className="dashboard-summary__header">
              <div className="dashboard-summary-card__copy">
                <span className="dashboard-kicker">Family</span>
                <h2 className="dashboard-section__title">{docs.family || snapshot.prompt_family}</h2>
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
              <h2 className="dashboard-section__title">필요한 링크로 이동</h2>
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
                <span className="dashboard-kicker">Snapshot</span>
                <h2 className="dashboard-section__title">현재 상태 스냅샷</h2>
              </div>
            </div>
            {docs.snapshotItems.length > 0 ? (
              <ul className="promptops-list">
                {docs.snapshotItems.map((item) => (
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
                <span className="dashboard-kicker">Interpretation</span>
                <h2 className="dashboard-section__title">현재 해석</h2>
              </div>
            </div>
            {docs.interpretation.length > 0 ? (
              <ul className="promptops-list">
                {docs.interpretation.map((item) => (
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
                <span className="dashboard-kicker">Iteration</span>
                <h2 className="dashboard-section__title">최신 iteration 기록</h2>
              </div>
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
            <div className="dashboard-section__header">
              <div>
                <span className="dashboard-kicker">Backlog</span>
                <h2 className="dashboard-section__title">다음 backlog</h2>
              </div>
            </div>
            {snapshot.next_backlog_items.length > 0 ? (
              <ul className="promptops-list promptops-list--links">
                {snapshot.next_backlog_items.map((item) => (
                  <li key={item.url}>
                    <Link href={item.url} rel="noreferrer" target="_blank">
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

        <section className="dashboard-card promptops-card">
          <div className="dashboard-section__header">
            <div>
              <span className="dashboard-kicker">Reference</span>
              <h2 className="dashboard-section__title">운영 참고 링크</h2>
            </div>
          </div>
          {docs.referenceLinks.length > 0 ? (
            <ul className="promptops-list promptops-list--links">
              {docs.referenceLinks.map((item) => (
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
          {docs.usageNotes.length > 0 ? (
            <>
              <p className="dashboard-meta">운영 순서</p>
              <ol className="promptops-numbered-list">
                {docs.usageNotes.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ol>
            </>
          ) : null}
        </section>
      </div>
    </main>
  );
}
