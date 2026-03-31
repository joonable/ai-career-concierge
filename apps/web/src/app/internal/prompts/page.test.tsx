import React from "react";
import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import InternalPromptsPage from "@/app/internal/prompts/page";

const loadPromptOpsWorkspaceData = vi.fn();
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
  loadPromptOpsWorkspaceData: (...args: unknown[]) => loadPromptOpsWorkspaceData(...args),
}));

vi.mock("@/lib/promptops_access", () => ({
  ensurePromptOpsAdminAccess: (...args: unknown[]) => ensurePromptOpsAdminAccess(...args),
}));

describe("InternalPromptsPage", () => {
  beforeEach(() => {
    loadPromptOpsWorkspaceData.mockReset();
    ensurePromptOpsAdminAccess.mockReset();
    ensurePromptOpsAdminAccess.mockResolvedValue(undefined);
  });

  it("renders the prompt workspace with lineage and links", async () => {
    loadPromptOpsWorkspaceData.mockResolvedValue({
      status: "ready",
      docs: {
        updatedAt: "2026-03-31 (Asia/Seoul)",
        family: "job-evaluation",
        snapshotItems: ["현재 production tag: job-evaluation:latest"],
        interpretation: ["candidate 유지"],
        usageNotes: ["compare 링크를 확인한다."],
        referenceLinks: [{ label: "compare link", url: "https://smith.langchain.com/compare" }],
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
    });

    render(await InternalPromptsPage());

    expect(screen.getByText("프롬프트 운영 패널")).toBeInTheDocument();
    expect(screen.getByText("job-evaluation:latest")).toBeInTheDocument();
    expect(screen.getByText("Compare 실험 보기")).toBeInTheDocument();
    expect(screen.getByText("fit_score_band 개선")).toBeInTheDocument();
    expect(screen.getByText("Role alignment")).toBeInTheDocument();
    expect(screen.getByText("compare link")).toBeInTheDocument();
  });

  it("renders an in-page error state when loading fails", async () => {
    loadPromptOpsWorkspaceData.mockResolvedValue({
      status: "error",
      message: "PromptOps 운영 상태를 불러오지 못했습니다.",
    });

    render(await InternalPromptsPage());

    expect(screen.getByText("대시보드를 불러오지 못했습니다")).toBeInTheDocument();
    expect(screen.getByText("PromptOps 운영 상태를 불러오지 못했습니다.")).toBeInTheDocument();
  });
});
