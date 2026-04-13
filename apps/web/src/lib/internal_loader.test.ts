import { beforeEach, describe, expect, it, vi } from "vitest";

import { loadInternalPageData, loadPromptOpsWorkspaceData } from "@/lib/internal_loader";

const loadInternalStatusDocument = vi.fn();
const loadPromptOpsDocumentSummary = vi.fn();
const getPromptOpsStatusSnapshot = vi.fn();
const getPromptOpsDatasetSnapshot = vi.fn();

vi.mock("@/lib/internal_docs", () => ({
  loadInternalStatusDocument: (...args: unknown[]) => loadInternalStatusDocument(...args),
  loadPromptOpsDocumentSummary: (...args: unknown[]) => loadPromptOpsDocumentSummary(...args),
}));

vi.mock("@/lib/api_client_server", () => ({
  getPromptOpsStatusSnapshot: (...args: unknown[]) => getPromptOpsStatusSnapshot(...args),
  getPromptOpsDatasetSnapshot: (...args: unknown[]) => getPromptOpsDatasetSnapshot(...args),
}));

const mockDocs = {
  updatedAt: "2026-04-12 (Asia/Seoul)",
  family: "job-evaluation",
  snapshotItems: [],
  interpretation: [],
  usageNotes: [],
  referenceLinks: [],
};

const mockSnapshot = {
  prompt_family: "job-evaluation",
  production_identifier: "job-evaluation:latest",
  staging_identifier: "job-evaluation:staging",
  candidate_identifier: "job-evaluation · local-dev-preview",
  latest_decision: "dev preview 모드: 문서/fixture 기반으로 운영 화면만 확인 중",
  compare_url: "",
  review_queue_name: "job-evaluation-review",
  review_queue_url: "",
  notion_backlog_url: "",
  latest_iteration_title: "Job Evaluation Iteration 001",
  latest_iteration_url: "/internal/prompts/iterations/job-evaluation-001",
  latest_summary: [],
  next_backlog_items: [],
};

const mockDataset = {
  total: 2,
  items: [
    {
      id: "item-001",
      scenario_type: "강한_일치",
      scenario_family: "직접_mle_일치",
      difficulty: "쉬움",
      should_pass: true,
      fit_score_min: 80,
      fit_score_max: 100,
      scoring_note: "직접 역할 일치",
      job_title: "시니어 머신러닝 엔지니어",
    },
    {
      id: "item-002",
      scenario_type: "딜브레이커",
      scenario_family: "온사이트_전용",
      difficulty: "쉬움",
      should_pass: false,
      fit_score_min: 0,
      fit_score_max: 0,
      scoring_note: "딜브레이커 트리거",
      job_title: "데이터 사이언티스트",
    },
  ],
};

describe("internal loader", () => {
  const originalBypass = process.env.PROMPTOPS_DEV_BYPASS;

  beforeEach(() => {
    loadInternalStatusDocument.mockReset();
    loadPromptOpsDocumentSummary.mockReset();
    getPromptOpsStatusSnapshot.mockReset();
    getPromptOpsDatasetSnapshot.mockReset();
    process.env.PROMPTOPS_DEV_BYPASS = originalBypass;
    vi.unstubAllEnvs();
  });

  it("returns a dev mock snapshot for the internal hub when bypass is enabled", async () => {
    process.env.PROMPTOPS_DEV_BYPASS = "true";
    vi.stubEnv("NODE_ENV", "development");
    loadInternalStatusDocument.mockResolvedValue({
      updatedAt: "2026-04-12 (Asia/Seoul)",
      operationsAgent: [],
      userProductUX: [],
      milestones: [],
      actions: [],
      recentCompletions: [],
      backlog: [],
      notes: [],
      references: [],
      coreDocuments: [],
    });
    loadPromptOpsDocumentSummary.mockResolvedValue(mockDocs);
    getPromptOpsStatusSnapshot.mockRejectedValue(new Error("No active Supabase session."));

    await expect(loadInternalPageData()).resolves.toMatchObject({
      status: "ready",
      promptSummary: {
        snapshot: {
          latest_decision: "dev preview 모드: 문서/fixture 기반으로 운영 화면만 확인 중",
        },
      },
    });
  });

  it("returns a dev mock snapshot for the prompt workspace when bypass is enabled", async () => {
    process.env.PROMPTOPS_DEV_BYPASS = "true";
    vi.stubEnv("NODE_ENV", "development");
    loadPromptOpsDocumentSummary.mockResolvedValue(mockDocs);
    getPromptOpsStatusSnapshot.mockRejectedValue(new Error("No active Supabase session."));

    await expect(loadPromptOpsWorkspaceData()).resolves.toMatchObject({
      status: "ready",
      snapshot: {
        candidate_identifier: "job-evaluation · local-dev-preview",
      },
    });
  });

  it("includes dataset in prompt workspace data when fetch succeeds", async () => {
    loadPromptOpsDocumentSummary.mockResolvedValue(mockDocs);
    getPromptOpsStatusSnapshot.mockResolvedValue(mockSnapshot);
    getPromptOpsDatasetSnapshot.mockResolvedValue(mockDataset);

    await expect(loadPromptOpsWorkspaceData()).resolves.toMatchObject({
      status: "ready",
      dataset: {
        total: 2,
        items: expect.arrayContaining([
          expect.objectContaining({ should_pass: true }),
          expect.objectContaining({ should_pass: false }),
        ]),
      },
    });
  });

  it("returns null dataset when dataset fetch fails", async () => {
    loadPromptOpsDocumentSummary.mockResolvedValue(mockDocs);
    getPromptOpsStatusSnapshot.mockResolvedValue(mockSnapshot);
    getPromptOpsDatasetSnapshot.mockRejectedValue(new Error("dataset unavailable"));

    await expect(loadPromptOpsWorkspaceData()).resolves.toMatchObject({
      status: "ready",
      dataset: null,
    });
  });
});
