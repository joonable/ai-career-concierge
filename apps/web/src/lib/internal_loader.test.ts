import { beforeEach, describe, expect, it, vi } from "vitest";

import { loadInternalPageData, loadPromptOpsWorkspaceData } from "@/lib/internal_loader";

const loadInternalStatusDocument = vi.fn();
const loadPromptOpsDocumentSummary = vi.fn();
const getPromptOpsStatusSnapshot = vi.fn();

vi.mock("@/lib/internal_docs", () => ({
  loadInternalStatusDocument: (...args: unknown[]) => loadInternalStatusDocument(...args),
  loadPromptOpsDocumentSummary: (...args: unknown[]) => loadPromptOpsDocumentSummary(...args),
}));

vi.mock("@/lib/api_client_server", () => ({
  getPromptOpsStatusSnapshot: (...args: unknown[]) => getPromptOpsStatusSnapshot(...args),
}));

describe("internal loader", () => {
  const originalBypass = process.env.PROMPTOPS_DEV_BYPASS;

  beforeEach(() => {
    loadInternalStatusDocument.mockReset();
    loadPromptOpsDocumentSummary.mockReset();
    getPromptOpsStatusSnapshot.mockReset();
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
    loadPromptOpsDocumentSummary.mockResolvedValue({
      updatedAt: "2026-04-12 (Asia/Seoul)",
      family: "job-evaluation",
      snapshotItems: [],
      interpretation: [],
      usageNotes: [],
      referenceLinks: [],
    });
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
    loadPromptOpsDocumentSummary.mockResolvedValue({
      updatedAt: "2026-04-12 (Asia/Seoul)",
      family: "job-evaluation",
      snapshotItems: [],
      interpretation: [],
      usageNotes: [],
      referenceLinks: [],
    });
    getPromptOpsStatusSnapshot.mockRejectedValue(new Error("No active Supabase session."));

    await expect(loadPromptOpsWorkspaceData()).resolves.toMatchObject({
      status: "ready",
      snapshot: {
        candidate_identifier: "job-evaluation · local-dev-preview",
      },
    });
  });
});
