import { redirect } from "next/navigation";

export default async function PromptOpsPage() {
  redirect("/internal/prompts");
}
