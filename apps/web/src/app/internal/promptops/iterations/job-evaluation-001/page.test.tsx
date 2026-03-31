import { describe, expect, it, vi } from "vitest";

import PromptOpsLegacyIterationRedirectPage from "@/app/internal/promptops/iterations/job-evaluation-001/page";

const redirect = vi.fn();

vi.mock("next/navigation", () => ({
  redirect: (...args: unknown[]) => redirect(...args),
}));

describe("PromptOps legacy iteration route", () => {
  it("redirects to the new iteration detail route", async () => {
    await PromptOpsLegacyIterationRedirectPage();

    expect(redirect).toHaveBeenCalledWith("/internal/prompts/iterations/job-evaluation-001");
  });
});
