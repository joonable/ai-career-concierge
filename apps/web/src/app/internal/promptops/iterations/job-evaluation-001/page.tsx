import { redirect } from "next/navigation";

export default async function PromptOpsLegacyIterationRedirectPage() {
  redirect("/internal/prompts/iterations/job-evaluation-001");
}
