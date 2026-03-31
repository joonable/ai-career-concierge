import Link from "next/link";
import React from "react";

import { DashboardErrorState } from "@/components/dashboard/dashboard-error-state";
import { ensurePromptOpsAdminAccess } from "@/lib/promptops_access";
import { loadInternalPageData } from "@/lib/internal_loader";
import { WorkboardCard } from "@/components/internal/WorkboardCard";
import { CoreDocsCard } from "@/components/internal/CoreDocsCard";

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
        
        {/* Top Hero Section */}
        <section className="dashboard-grid promptops-overview-grid">
          <article className="dashboard-card dashboard-card--active dashboard-card--span-2">
            <div className="dashboard-hero">
              <div className="dashboard-hero__top">
                <div className="dashboard-hero__copy">
                  <span className="dashboard-kicker">Internal</span>
                  <h1 className="dashboard-title">운영 허브</h1>
                  <p className="dashboard-subcopy">
                    제품의 진행 상황과 파이프라인 운영 상태를 모니터링하고 핵심 문서를 바로 읽어볼 수 있는 통합 상황판입니다.
                  </p>
                </div>
                <span className="dashboard-pill dashboard-pill--accent">
                  {internalStatus.updatedAt || "문서 갱신 대기"}
                </span>
              </div>
              <div className="dashboard-stat-grid">
                <div className="dashboard-stat">
                  <span className="dashboard-stat__label">시스템 운영 과제</span>
                  <strong>{internalStatus.operationsAgent.length || 0}</strong>
                </div>
                <div className="dashboard-stat">
                  <span className="dashboard-stat__label">제품/유저 과제</span>
                  <strong>{internalStatus.userProductUX.length || 0}</strong>
                </div>
                <div className="dashboard-stat">
                  <span className="dashboard-stat__label">Open actions</span>
                  <strong>{internalStatus.actions.length || 0}</strong>
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
            <p className="dashboard-meta" style={{ marginBottom: "12px", marginTop: "4px" }}>
              최신 결정: {promptSummary.snapshot.latest_decision || FALLBACK_VALUE}
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
            <div className="dashboard-summary-card__footer" style={{ marginTop: "auto" }}>
              <span className="dashboard-summary-card__cta">PromptOps 뷰어로 이동</span>
              <span className="dashboard-summary-card__arrow" aria-hidden="true">
                →
              </span>
            </div>
          </Link>
        </section>

        {/* Asymmetric Dashboard Body */}
        <div className="dashboard-grid promptops-overview-grid" style={{ alignItems: "start", marginTop: "16px" }}>
          
          {/* Main Column (Workboard) */}
          <div className="dashboard-card--span-2" style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
            <WorkboardCard kicker="Operations & Agent" title="시스템 및 에이전트 관점" type="current" items={internalStatus.operationsAgent} />
            <WorkboardCard kicker="User & Product UX" title="유저 및 제품 관점" type="next" items={internalStatus.userProductUX} />
            
            <details className="dashboard-accordion" style={{ outline: "none", cursor: "pointer", marginTop: "8px" }}>
              <summary style={{ padding: "0 8px 12px", fontSize: "0.95rem", color: "#9ca3af", userSelect: "none" }}>
                최근 완료 작업 ({internalStatus.recentCompletions.length}건) 펼쳐보기
              </summary>
              <div style={{ paddingBottom: "8px" }}>
                <WorkboardCard kicker="Done" title="최근 완료 작업" type="done" items={internalStatus.recentCompletions} />
              </div>
            </details>
          </div>

          {/* Sidebar Column (Docs, Milestones, Backlogs) */}
          <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
            <CoreDocsCard kicker="Core Docs" title="핵심 문서 레지스트리" items={internalStatus.coreDocuments} />
            <CoreDocsCard kicker="References" title="참고 링크" items={internalStatus.references} />
            
            <WorkboardCard kicker="Milestones" title="프로젝트 진행 상황" type="milestone" items={internalStatus.milestones} />
            <WorkboardCard kicker="Next Action" title="다음 해야 할 action" type="next" items={internalStatus.actions} />
            <WorkboardCard kicker="Backlog" title="앞으로의 backlog" type="backlog" items={internalStatus.backlog} />
            <WorkboardCard kicker="Notes" title="운영 메모" type="note" items={internalStatus.notes} />
          </div>

        </div>
      </div>
    </main>
  );
}
