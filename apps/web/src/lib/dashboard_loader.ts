import { getDashboardSnapshot, getProfileSnapshot } from "@/lib/api_client_server";
import { DashboardDataError } from "@/lib/dashboard_errors";
import type { DashboardResponse } from "@/lib/dashboard_types";
import type { UserProfileResponse } from "@/lib/profile_types";

type DashboardPageDataSuccess = {
  status: "ready";
  dashboard: DashboardResponse;
  profile: UserProfileResponse;
};

type DashboardPageDataFailure = {
  status: "error";
  message: string;
};

export type DashboardPageData = DashboardPageDataSuccess | DashboardPageDataFailure;

export async function loadDashboardPageData(): Promise<DashboardPageData> {
  try {
    const [dashboard, profile] = await Promise.all([getDashboardSnapshot(), getProfileSnapshot()]);
    return {
      status: "ready",
      dashboard,
      profile,
    };
  } catch (error) {
    return {
      status: "error",
      message: normalizeDashboardErrorMessage(error),
    };
  }
}

function normalizeDashboardErrorMessage(error: unknown) {
  if (error instanceof DashboardDataError) {
    return error.message;
  }

  if (error instanceof Error && error.message.trim().length > 0) {
    return error.message;
  }

  return "대시보드 데이터를 불러오지 못했습니다. 잠시 후 다시 시도해 주세요.";
}
