import { describe, expect, it } from "vitest";

import { loadInternalStatusDocument, loadPromptOpsDocumentSummary } from "@/lib/internal_docs";

describe("internal docs parsing", () => {
  it("parses the repository internal status document into dashboard sections", async () => {
    const result = await loadInternalStatusDocument();

    expect(result.operationsAgent[0]).toContain("PromptOps lineage");
    expect(result.userProductUX[0]).toContain("수직 슬라이스");
    expect(result.recentCompletions[0]).toContain("리디자인");
    expect(result.actions[0]).toContain("Markdown 뷰어");
    expect(result.backlog[0]).toContain("Scraper 상태를 모니터링");
    expect(result.notes[0]).toContain("캐시");
    expect(result.references).toEqual(expect.arrayContaining([
      { label: "AGENTS.md", url: "/internal/docs/AGENTS.md" },
      { label: "프로젝트 컨텍스트", url: "/internal/docs/CONTEXT.md" },
    ]));
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
        url: "/internal/docs/iterations/job_evaluation_iteration_001.md",
      },
      {
        label: "Notion backlog: PromptOps Backlog",
        url: "https://www.notion.so/c5fb7393ece54107b445e90bdabab642",
      },
    ]);
  });
});
