import { getPromptOpsStatusSnapshot } from "@/lib/api_client_server";
import { DashboardDataError } from "@/lib/dashboard_errors";
import type { PromptOpsStatusResponse } from "@/lib/promptops_types";

type PromptOpsPageDataSuccess = {
  status: "ready";
  snapshot: PromptOpsStatusResponse;
};

type PromptOpsPageDataFailure = {
  status: "error";
  message: string;
};

export type PromptOpsPageData = PromptOpsPageDataSuccess | PromptOpsPageDataFailure;

export async function loadPromptOpsPageData(): Promise<PromptOpsPageData> {
  try {
    return {
      status: "ready",
      snapshot: await getPromptOpsStatusSnapshot(),
    };
  } catch (error) {
    return {
      status: "error",
      message: normalizePromptOpsErrorMessage(error),
    };
  }
}

function normalizePromptOpsErrorMessage(error: unknown) {
  if (error instanceof DashboardDataError) {
    return error.message;
  }

  if (error instanceof Error && error.message.trim().length > 0) {
    return error.message;
  }

  return "PromptOps 운영 상태를 불러오지 못했습니다. 잠시 후 다시 시도해 주세요.";
}
