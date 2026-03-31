import { DashboardDataError } from "@/lib/dashboard_errors";
import {
  loadInternalStatusDocument,
  loadPromptOpsDocumentSummary,
  type InternalStatusDocument,
  type PromptOpsDocumentSummary,
} from "@/lib/internal_docs";
import { getPromptOpsStatusSnapshot } from "@/lib/api_client_server";
import type { PromptOpsStatusResponse } from "@/lib/promptops_types";

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

    return {
      status: "ready",
      docs,
      snapshot,
    };
  } catch (error) {
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
