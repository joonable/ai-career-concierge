import React from "react";
import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import PromptOpsPage from "@/app/internal/promptops/page";

const loadPromptOpsPageData = vi.fn();
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

vi.mock("@/lib/promptops_loader", () => ({
  loadPromptOpsPageData: (...args: unknown[]) => loadPromptOpsPageData(...args),
}));

vi.mock("@/lib/promptops_access", () => ({
  ensurePromptOpsAdminAccess: (...args: unknown[]) => ensurePromptOpsAdminAccess(...args),
}));

describe("PromptOpsPage", () => {
  beforeEach(() => {
    loadPromptOpsPageData.mockReset();
    ensurePromptOpsAdminAccess.mockReset();
    ensurePromptOpsAdminAccess.mockResolvedValue(undefined);
  });

  it("renders the internal PromptOps panel summary", async () => {
    loadPromptOpsPageData.mockResolvedValue({
      status: "ready",
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
        latest_iteration_url: "/internal/promptops/iterations/job-evaluation-001",
        latest_summary: ["fit_score_band 개선"],
        next_backlog_items: [{ title: "Role alignment", url: "https://notion.so/item-1" }],
      },
    });

    render(await PromptOpsPage());

    expect(screen.getByText("운영 패널")).toBeInTheDocument();
    expect(screen.getByText("candidate 유지")).toBeInTheDocument();
    expect(screen.getByText("job-evaluation:latest")).toBeInTheDocument();
    expect(screen.getByText("Review Queue (job-evaluation-review)")).toBeInTheDocument();
    expect(screen.getByText("Role alignment")).toBeInTheDocument();
  });

  it("renders an in-page error state when data loading fails", async () => {
    loadPromptOpsPageData.mockResolvedValue({
      status: "error",
      message: "PromptOps 운영 상태를 불러오지 못했습니다.",
    });

    render(await PromptOpsPage());

    expect(screen.getByText("대시보드를 불러오지 못했습니다")).toBeInTheDocument();
    expect(screen.getByText("PromptOps 운영 상태를 불러오지 못했습니다.")).toBeInTheDocument();
  });
});
