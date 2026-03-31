import { notFound } from "next/navigation";

import { createSupabaseServerClient } from "@/lib/supabase_auth_server";

function getAllowedPromptOpsEmails(): string[] {
  const raw = process.env.PROMPTOPS_ADMIN_EMAILS ?? "";
  return raw
    .split(",")
    .map((value) => value.trim().toLowerCase())
    .filter((value, index, items) => value.length > 0 && items.indexOf(value) === index);
}

export async function ensurePromptOpsAdminAccess(): Promise<void> {
  const allowedEmails = getAllowedPromptOpsEmails();
  if (allowedEmails.length === 0) {
    notFound();
  }

  const supabase = await createSupabaseServerClient();
  const {
    data: { session },
  } = await supabase.auth.getSession();
  const email = session?.user?.email?.trim().toLowerCase();

  if (!email || !allowedEmails.includes(email)) {
    notFound();
  }
}

export function isPromptOpsAdminEmail(email: string | null | undefined): boolean {
  const allowedEmails = getAllowedPromptOpsEmails();
  if (allowedEmails.length === 0 || !email) {
    return false;
  }

  return allowedEmails.includes(email.trim().toLowerCase());
}
