import { describe, expect, it } from "vitest";

import { loadInternalStatusDocument, loadPromptOpsDocumentSummary } from "@/lib/internal_docs";

describe("internal docs parsing", () => {
  it("parses the repository internal status document into dashboard sections", async () => {
    const result = await loadInternalStatusDocument();

    expect(result.updatedAt).toBe("2026-03-31 (Asia/Seoul)");
    expect(result.currentFocus).toContain("/internal 운영 허브와 /internal/prompts 전용 작업대 분리");
    expect(result.milestones).toContain("Internal 운영 허브 정보 구조 정리: 진행 중");
    expect(result.actions).toContain("milestone과 backlog를 문서 기준으로 계속 갱신");
    expect(result.backlog).toContain("prompt family가 늘어나도 /internal/prompts 카드 구조를 그대로 재사용할 수 있게 확장");
    expect(result.notes).toContain("운영 상태의 canonical source는 docs 문서로 유지");
    expect(result.references).toEqual([
      { label: "PromptOps 기준서", url: "../promptops/README.md" },
      { label: "PromptOps 현재 상태", url: "../promptops/status.md" },
      { label: "Iteration 001 기록", url: "../promptops/iterations/job_evaluation_iteration_001.md" },
      { label: "운영 패널 문서 계약", url: "./operations_panel.md" },
      { label: "에이전트 작업 보드", url: "./agent_workboard.md" },
    ]);
  });

  it("parses the repository promptops status document into prompt workspace sections", async () => {
    const result = await loadPromptOpsDocumentSummary();

    expect(result.updatedAt).toBe("2026-03-31 (Asia/Seoul)");
    expect(result.family).toBe("job-evaluation");
    expect(result.snapshotItems).toContain("현재 production tag: job-evaluation:latest");
    expect(result.interpretation).toContain("최신 staging 프롬프트는 점수 밴드와 분류 일관성은 충분히 안정적인 편입니다.");
    expect(result.usageNotes).toContain("compare 링크를 열어 baseline/candidate 차이를 본다.");
    expect(result.referenceLinks).toEqual([
      {
        label: "직전 candidate vs 최신 staging 검증 compare: compare link",
        url: "https://smith.langchain.com/o/a5f5f699-f384-58ec-9be0-2a39bb96969e/datasets/277c4ae5-c460-4be4-8895-732911768cd7/compare?selectedSessions=4906f684-12db-4c1a-88d0-782d25f5bbda&selectedSessions=91e3e1bf-e2a1-426c-a155-ce616568eabd",
      },
      {
        label: "latest iteration report: job_evaluation_iteration_001.md",
        url: "./iterations/job_evaluation_iteration_001.md",
      },
      {
        label: "Notion backlog: PromptOps Backlog",
        url: "https://www.notion.so/c5fb7393ece54107b445e90bdabab642",
      },
    ]);
  });
});
