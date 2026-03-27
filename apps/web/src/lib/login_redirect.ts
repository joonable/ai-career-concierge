import { webEnv } from "@/lib/env";
import type { UserProfileResponse } from "@/lib/profile_types";

const DEFAULT_POST_LOGIN_PATH = "/dashboard";
const DEFAULT_ONBOARDING_PATH = "/onboarding";

export function resolveSafeNextPath(nextPath?: string | null): string | null {
  if (!nextPath) {
    return null;
  }

  if (!nextPath.startsWith("/") || nextPath.startsWith("//")) {
    return null;
  }

  return nextPath;
}

export function resolveProfileCompletionPath(profile: UserProfileResponse): string {
  return profile.profile_data.role.trim() ? DEFAULT_POST_LOGIN_PATH : DEFAULT_ONBOARDING_PATH;
}

export async function resolvePostLoginPath(
  accessToken: string,
  nextPath?: string | null,
): Promise<string> {
  const safeNextPath = resolveSafeNextPath(nextPath);
  if (safeNextPath) {
    return safeNextPath;
  }

  const response = await fetch(`${webEnv.apiBaseUrl}/api/v1/users/me/profile`, {
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
    cache: "no-store",
  });

  if (!response.ok) {
    return DEFAULT_ONBOARDING_PATH;
  }

  const profile = (await response.json()) as UserProfileResponse;
  return resolveProfileCompletionPath(profile);
}
