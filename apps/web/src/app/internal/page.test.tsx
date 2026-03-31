import React from "react";
import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import InternalHomePage from "@/app/internal/page";

const loadInternalPageData = vi.fn();
const ensurePromptOpsAdminAccess = vi.fn();

vi.mock("next/link", () => ({
  default: ({
    children,
    href,
    ...props
  }: React.AnchorHTMLAttributes<HTMLAnchorElement> & { href: string }) => (
    <a href={href} {...props}>
      {children}
    </a>
  ),
}));

vi.mock("@/lib/internal_loader", () => ({
  loadInternalPageData: (...args: unknown[]) => loadInternalPageData(...args),
}));

vi.mock("@/lib/promptops_access", () => ({
  ensurePromptOpsAdminAccess: (...args: unknown[]) => ensurePromptOpsAdminAccess(...args),
}));

describe("InternalHomePage", () => {
  beforeEach(() => {
    loadInternalPageData.mockReset();
    ensurePromptOpsAdminAccess.mockReset();
    ensurePromptOpsAdminAccess.mockResolvedValue(undefined);
  });

  it("renders the internal operations hub with docs and prompt summary", async () => {
    loadInternalPageData.mockResolvedValue({
      status: "ready",
      internalStatus: {
        updatedAt: "2026-03-31 (Asia/Seoul)",
        currentFocus: ["운영 허브 정보 구조 정리"],
        milestones: ["internal 운영 허브: 진행 중"],
        actions: ["docs 기반 상태 카드 보강"],
        recentCompletions: ["운영 패널 문서 계약 정리"],
        backlog: ["Prompt family 확장 준비"],
        notes: ["운영 상태는 docs를 canonical source로 유지"],
        references: [{ label: "PromptOps 기준서", url: "https://example.com/promptops" }],
        coreDocuments: [{ label: "AGENTS.md", url: "/docs/AGENTS.md" }],
      },
      promptSummary: {
        docs: {
          updatedAt: "2026-03-31 (Asia/Seoul)",
          family: "job-evaluation",
          snapshotItems: [],
          interpretation: ["candidate 유지"],
          usageNotes: [],
          referenceLinks: [],
        },
        snapshot: {
          prompt_family: "job-evaluation",
          production_identifier: "job-evaluation:latest",
          staging_identifier: "job-evaluation:staging",
          candidate_identifier: "job-evaluation · local-v4",
          latest_decision: "candidate 유지",
          compare_url: "https://smith.langchain.com/compare",
          review_queue_name: "job-evaluation-review",
          review_queue_url: "https://smith.langchain.com/annotation-queues/1",
          notion_backlog_url: "https://notion.so/backlog",
          latest_iteration_title: "Job Evaluation Iteration 001",
          latest_iteration_url: "/internal/prompts/iterations/job-evaluation-001",
          latest_summary: ["fit_score_band 개선"],
          next_backlog_items: [{ title: "Role alignment", url: "https://notion.so/item-1" }],
        },
      },
    });

    render(await InternalHomePage());

    expect(screen.getByText("운영 허브")).toBeInTheDocument();
    expect(screen.getByText("운영 허브 정보 구조 정리")).toBeInTheDocument();
    expect(screen.getByText("운영 패널 문서 계약 정리")).toBeInTheDocument();
    expect(screen.getByText("internal 운영 허브: 진행 중")).toBeInTheDocument();
    expect(screen.getByText("AGENTS.md")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /프롬프트 운영 패널/i })).toHaveAttribute(
      "href",
      "/internal/prompts",
    );
    expect(screen.getByText("PromptOps 기준서")).toBeInTheDocument();
  });

  it("renders an in-page error state when loading fails", async () => {
    loadInternalPageData.mockResolvedValue({
      status: "error",
      message: "내부 운영 상태를 불러오지 못했습니다.",
    });

    render(await InternalHomePage());

    expect(screen.getByText("대시보드를 불러오지 못했습니다")).toBeInTheDocument();
    expect(screen.getByText("내부 운영 상태를 불러오지 못했습니다.")).toBeInTheDocument();
  });
});
