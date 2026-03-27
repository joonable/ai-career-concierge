import { createSupabaseServerClient } from "@/lib/supabase_auth_server";
import { webEnv } from "@/lib/env";
import type { UserProfileResponse } from "@/lib/profile_types";

type DashboardResponse = {
  user_id: string;
  minimum_fit_score: number;
  recommendations: Array<{
    evaluation_id: string;
    status: string;
    fit_score: number | null;
    reasoning: string | null;
    user_feedback: string | null;
    feedback_reason: string | null;
    job_id: string;
    title: string;
    company: string;
    url: string;
    platform: string;
  }>;
};

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

export async function getProfileSnapshot(): Promise<UserProfileResponse> {
  const accessToken = await getAccessToken();
  const response = await fetch(`${webEnv.apiBaseUrl}/api/v1/users/me/profile`, {
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error("Failed to load profile.");
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
    throw new Error("Failed to load dashboard.");
  }

  return response.json();
}
