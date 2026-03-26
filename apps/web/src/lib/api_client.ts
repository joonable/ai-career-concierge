import { webEnv } from "@/lib/env";

export type UserProfilePayload = {
  profile_data: Record<string, unknown>;
  guidelines: Record<string, unknown>;
  notification_settings: Record<string, unknown>;
};

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

function buildHeaders() {
  return {
    Authorization: "Bearer dev-token",
    "Content-Type": "application/json",
    "X-User-Email": "scaffold-user@example.com",
  };
}

export async function updateProfile(payload: UserProfilePayload) {
  const response = await fetch(`${webEnv.apiBaseUrl}/api/v1/users/me/profile`, {
    method: "PUT",
    headers: buildHeaders(),
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error("Failed to update profile.");
  }

  return response.json();
}

export async function getDashboardSnapshot(): Promise<DashboardResponse> {
  try {
    const response = await fetch(`${webEnv.apiBaseUrl}/api/v1/users/me/dashboard`, {
      headers: buildHeaders(),
      cache: "no-store",
    });

    if (!response.ok) {
      throw new Error("Failed to load dashboard.");
    }

    return response.json();
  } catch {
    return {
      user_id: "scaffold-user",
      minimum_fit_score: 80,
      recommendations: [],
    };
  }
}
