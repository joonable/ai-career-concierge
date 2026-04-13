const isTestEnvironment = process.env.NODE_ENV === "test" || process.env.VITEST === "true";

function readRequiredPublicEnv(name: string, value: string | undefined, fallbackForTests: string) {
  const trimmed = value?.trim();
  if (trimmed) {
    return trimmed;
  }

  if (isTestEnvironment) {
    return fallbackForTests;
  }

  throw new Error(
    `[web env] Missing required env ${name}. Run scripts/start_agent_task.sh again or define it in apps/web/.env.development.local.`,
  );
}

const API_BASE_URL = readRequiredPublicEnv("NEXT_PUBLIC_API_BASE_URL", process.env.NEXT_PUBLIC_API_BASE_URL, "http://localhost:8000");
const SUPABASE_URL = readRequiredPublicEnv("NEXT_PUBLIC_SUPABASE_URL", process.env.NEXT_PUBLIC_SUPABASE_URL, "https://example.supabase.co");
const SUPABASE_ANON_KEY = readRequiredPublicEnv("NEXT_PUBLIC_SUPABASE_ANON_KEY", process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY, "demo-anon-key");

export const webEnv = {
  apiBaseUrl: API_BASE_URL,
  supabaseUrl: SUPABASE_URL,
  supabaseAnonKey: SUPABASE_ANON_KEY,
};
