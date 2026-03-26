import { createClient } from "@supabase/supabase-js";

import { webEnv } from "@/lib/env";

export function createSupabaseBrowserClient() {
  return createClient(webEnv.supabaseUrl, webEnv.supabaseAnonKey, {
    auth: {
      persistSession: true,
      autoRefreshToken: true,
    },
  });
}
