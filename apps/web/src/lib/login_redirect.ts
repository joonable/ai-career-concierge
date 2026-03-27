const DEFAULT_POST_LOGIN_PATH = "/dashboard";

export function resolveSafeNextPath(nextPath?: string | null): string | null {
  if (!nextPath) {
    return null;
  }

  if (!nextPath.startsWith("/") || nextPath.startsWith("//")) {
    return null;
  }

  return nextPath;
}

export async function resolvePostLoginPath(
  accessToken: string,
  nextPath?: string | null,
): Promise<string> {
  void accessToken;
  const safeNextPath = resolveSafeNextPath(nextPath);
  if (safeNextPath) {
    return safeNextPath;
  }
  return DEFAULT_POST_LOGIN_PATH;
}
