import { describe, expect, it } from "vitest";

import { loadInternalStatusDocument, loadPromptOpsDocumentSummary } from "@/lib/internal_docs";

describe("internal docs parsing", () => {
  it("parses the repository internal status document into dashboard sections", async () => {
    const result = await loadInternalStatusDocument();

    expect(result.operationsAgent[0]).toContain("PromptOps lineage");
    expect(result.userProductUX[0]).toContain("수직 슬라이스");
    expect(result.recentCompletions[0]).toContain("리디자인");
    expect(result.actions[0]).toContain("Phase 4-1");
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
    expect(result.interpretation).toContain("현재의 \"실패\"는 프롬프트의 논리적 오류보다는 평가 지표(Metric)와 모델 답변 간의 언어 불일치에서 기인한 것이 많습니다.");
    expect(result.usageNotes).toContain("compare 링크를 열어 baseline/candidate 차이를 본다.");
    expect(result.referenceLinks).toEqual([
      {
        label: "최신 자동화 실험 리포트: iteration_002-final.md",
        url: "/internal/docs/iterations/iteration_002-final.md",
      },
      {
        label: "Notion backlog: PromptOps Backlog",
        url: "https://www.notion.so/c5fb7393ece54107b445e90bdabab642",
      },
    ]);
  });
});
