import { DashboardDataError } from "@/lib/dashboard_errors";
import {
  loadInternalStatusDocument,
  loadPromptOpsDocumentSummary,
  type InternalStatusDocument,
  type PromptOpsDocumentSummary,
} from "@/lib/internal_docs";
import { getPromptOpsDatasetSnapshot, getPromptOpsStatusSnapshot } from "@/lib/api_client_server";
import type { PromptOpsDatasetResponse, PromptOpsStatusResponse } from "@/lib/promptops_types";

type InternalPageDataSuccess = {
  status: "ready";
  internalStatus: InternalStatusDocument;
  promptSummary: {
    docs: PromptOpsDocumentSummary;
    snapshot: PromptOpsStatusResponse;
  };
};

type InternalPageDataFailure = {
  status: "error";
  message: string;
};

type PromptOpsWorkspaceDataSuccess = {
  status: "ready";
  docs: PromptOpsDocumentSummary;
  snapshot: PromptOpsStatusResponse;
  dataset: PromptOpsDatasetResponse | null;
};

type PromptOpsWorkspaceDataFailure = {
  status: "error";
  message: string;
};

export type InternalPageData = InternalPageDataSuccess | InternalPageDataFailure;
export type PromptOpsWorkspaceData = PromptOpsWorkspaceDataSuccess | PromptOpsWorkspaceDataFailure;

export async function loadInternalPageData(): Promise<InternalPageData> {
  try {
    const [internalStatus, promptDocs, promptSnapshot] = await Promise.all([
      loadInternalStatusDocument(),
      loadPromptOpsDocumentSummary(),
      getPromptOpsStatusSnapshot(),
    ]);

    return {
      status: "ready",
      internalStatus,
      promptSummary: {
        docs: promptDocs,
        snapshot: promptSnapshot,
      },
    };
  } catch (error) {
    if (shouldUsePromptOpsDevMock(error)) {
      const [internalStatus, promptDocs] = await Promise.all([
        loadInternalStatusDocument(),
        loadPromptOpsDocumentSummary(),
      ]);

      return {
        status: "ready",
        internalStatus,
        promptSummary: {
          docs: promptDocs,
          snapshot: createPromptOpsDevMockSnapshot(),
        },
      };
    }

    return {
      status: "error",
      message: normalizeInternalErrorMessage(error),
    };
  }
}

export async function loadPromptOpsWorkspaceData(): Promise<PromptOpsWorkspaceData> {
  try {
    const [docs, snapshot] = await Promise.all([
      loadPromptOpsDocumentSummary(),
      getPromptOpsStatusSnapshot(),
    ]);

    let dataset: PromptOpsDatasetResponse | null = null;
    try {
      dataset = await getPromptOpsDatasetSnapshot();
    } catch {
      // dataset은 선택적 컨텍스트 - fetch 실패 시 null로 처리
    }

    return {
      status: "ready",
      docs,
      snapshot,
      dataset,
    };
  } catch (error) {
    if (shouldUsePromptOpsDevMock(error)) {
      const docs = await loadPromptOpsDocumentSummary();

      return {
        status: "ready",
        docs,
        snapshot: createPromptOpsDevMockSnapshot(),
        dataset: createPromptOpsDevMockDataset(),
      };
    }

    return {
      status: "error",
      message: normalizeInternalErrorMessage(error),
    };
  }
}

function normalizeInternalErrorMessage(error: unknown) {
  if (error instanceof DashboardDataError) {
    return error.message;
  }

  if (error instanceof Error && error.message.trim().length > 0) {
    return error.message;
  }

  return "내부 운영 상태를 불러오지 못했습니다. 잠시 후 다시 시도해 주세요.";
}

function shouldUsePromptOpsDevMock(error: unknown) {
  return (
    process.env.NODE_ENV !== "production" &&
    process.env.PROMPTOPS_DEV_BYPASS === "true" &&
    error instanceof Error &&
    error.message.includes("No active Supabase session.")
  );
}

function createPromptOpsDevMockSnapshot(): PromptOpsStatusResponse {
  return {
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
    latest_summary: [
      "현재 세션이 없으므로 PromptOps 운영 화면은 문서와 fixture 기준 mock snapshot으로 렌더링됩니다.",
      "실제 compare/review/backlog 링크는 로그인 후 runtime snapshot에서 확인할 수 있습니다.",
    ],
    next_backlog_items: [],
  };
}

function createPromptOpsDevMockDataset(): PromptOpsDatasetResponse {
  return {
    total: 3,
    items: [
      {
        id: "gold-001",
        scenario_type: "강한_일치",
        scenario_family: "직접_mle_일치",
        difficulty: "쉬움",
        should_pass: true,
        fit_score_min: 80,
        fit_score_max: 100,
        scoring_note: "직접적인 역할 일치 (dev mock)",
        job_title: "시니어 머신러닝 엔지니어",
      },
      {
        id: "gold-002",
        scenario_type: "딜브레이커",
        scenario_family: "계약직_전용",
        difficulty: "쉬움",
        should_pass: false,
        fit_score_min: 0,
        fit_score_max: 0,
        scoring_note: "딜브레이커 트리거 (dev mock)",
        job_title: "데이터 사이언티스트 (계약직)",
      },
      {
        id: "gold-003",
        scenario_type: "경계_사례",
        scenario_family: "인접_분석_인프라",
        difficulty: "보통",
        should_pass: false,
        fit_score_min: 40,
        fit_score_max: 59,
        scoring_note: "borderline 경계 사례 (dev mock)",
        job_title: "데이터 엔지니어",
      },
    ],
  };
}
