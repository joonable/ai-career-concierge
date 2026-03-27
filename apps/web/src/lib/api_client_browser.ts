"use client";

import { createSupabaseBrowserClient } from "@/lib/supabase_auth_browser";
import { webEnv } from "@/lib/env";
import type { UserProfilePayload, UserProfileResponse } from "@/lib/profile_types";

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

export async function getProfile(): Promise<UserProfileResponse> {
  const response = await fetch(`${webEnv.apiBaseUrl}/api/v1/users/me/profile`, {
    headers: await buildAuthenticatedHeaders(),
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error("Failed to load profile.");
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
    throw new Error("Failed to update profile.");
  }

  return response.json();
}
