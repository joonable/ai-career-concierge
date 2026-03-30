"use client";

import { createSupabaseBrowserClient } from "@/lib/supabase_auth_browser";
import { webEnv } from "@/lib/env";
import type { UserProfilePayload, UserProfileResponse } from "@/lib/profile_types";

export type FeedbackPayload = {
  feedback: "LIKE" | "DISLIKE" | "LATER";
  feedback_reason?: string | null;
};

async function buildAuthenticatedHeaders() {
  const supabase = createSupabaseBrowserClient();
  const {
    data: { session },
  } = await supabase.auth.getSession();

  if (!session?.access_token) {
    throw new Error("No active Supabase session.");
  }

  return {
    Authorization: `Bearer ${session.access_token}`,
    "Content-Type": "application/json",
  };
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
    // Ignore text parsing failures and return the fallback message.
  }

  return fallbackMessage;
}

export async function getProfile(): Promise<UserProfileResponse> {
  const response = await fetch(`${webEnv.apiBaseUrl}/api/v1/users/me/profile`, {
    headers: await buildAuthenticatedHeaders(),
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error(await readErrorMessage(response, "Failed to load profile."));
  }

  return response.json();
}

export async function updateProfile(payload: UserProfilePayload): Promise<UserProfileResponse> {
  const response = await fetch(`${webEnv.apiBaseUrl}/api/v1/users/me/profile`, {
    method: "PUT",
    headers: await buildAuthenticatedHeaders(),
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error(await readErrorMessage(response, "Failed to update profile."));
  }

  return response.json();
}

export async function recordEvaluationFeedback(
  evaluationId: string,
  payload: FeedbackPayload,
): Promise<{
  evaluation_id: string;
  feedback: FeedbackPayload["feedback"];
  feedback_reason: string | null;
}> {
  const response = await fetch(`${webEnv.apiBaseUrl}/api/v1/evaluations/${evaluationId}/feedback`, {
    method: "POST",
    headers: await buildAuthenticatedHeaders(),
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error(await readErrorMessage(response, "Failed to save feedback."));
  }

  return response.json();
}
