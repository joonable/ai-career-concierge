/**
 * Next.js App Router의 서버 컴포넌트(RSC) 환경에서 FastAPI 백엔드와 통신하는 유틸리티입니다.
 * Supabase Server Client를 통해 인증 토큰을 획득하며, 
 * 주로 페이지 렌더링을 위한 데이터 페칭(대시보드 목록, 프로필 조회 등)에 사용됩니다.
 */

import { createSupabaseServerClient } from "@/lib/supabase_auth_server";
import { DashboardDataError } from "@/lib/dashboard_errors";
import type { DashboardResponse } from "@/lib/dashboard_types";
import { webEnv } from "@/lib/env";
import type { PromptOpsStatusResponse } from "@/lib/promptops_types";
import type { UserProfileResponse } from "@/lib/profile_types";

async function getAccessToken(): Promise<string> {
  const supabase = await createSupabaseServerClient();
  const {
    data: { session },
  } = await supabase.auth.getSession();

  if (!session?.access_token) {
    throw new Error("No active Supabase session.");
  }

  return session.access_token;
}

async function readErrorMessage(response: Response, fallbackMessage: string) {
  try {
    const data = await response.json();
    if (typeof data?.detail === "string" && data.detail.trim().length > 0) {
      return data.detail;
    }
  } catch {
    // Ignore JSON parsing failures and fall back to text.
  }

  try {
    const text = await response.text();
    if (text.trim().length > 0) {
      return text;
    }
  } catch {
    // Ignore text parsing failures and use the fallback message.
  }

  return fallbackMessage;
}

export async function getProfileSnapshot(): Promise<UserProfileResponse> {
  const accessToken = await getAccessToken();
  const response = await fetch(`${webEnv.apiBaseUrl}/api/v1/users/me/profile`, {
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
    cache: "no-store",
  });

  if (!response.ok) {
    throw new DashboardDataError(
      await readErrorMessage(response, "프로필 데이터를 불러오지 못했습니다."),
    );
  }

  return response.json();
}

export async function getDashboardSnapshot(): Promise<DashboardResponse> {
  const accessToken = await getAccessToken();
  const response = await fetch(`${webEnv.apiBaseUrl}/api/v1/users/me/dashboard`, {
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
    cache: "no-store",
  });

  if (!response.ok) {
    throw new DashboardDataError(
      await readErrorMessage(response, "추천 대시보드를 불러오지 못했습니다."),
    );
  }

  return response.json();
}

export async function getPromptOpsStatusSnapshot(): Promise<PromptOpsStatusResponse> {
  const accessToken = await getAccessToken();
  const response = await fetch(`${webEnv.apiBaseUrl}/api/v1/users/me/promptops-status`, {
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
    cache: "no-store",
  });

  if (!response.ok) {
    throw new DashboardDataError(
      await readErrorMessage(response, "PromptOps 운영 상태를 불러오지 못했습니다."),
    );
  }

  return response.json();
}
