import { describe, expect, it, vi } from "vitest";

import PromptOpsRedirectPage from "@/app/internal/promptops/page";

const redirect = vi.fn();

vi.mock("next/navigation", () => ({
  redirect: (...args: unknown[]) => redirect(...args),
}));

describe("PromptOps legacy route", () => {
  it("redirects to the new prompts workspace", async () => {
    await PromptOpsRedirectPage();

    expect(redirect).toHaveBeenCalledWith("/internal/prompts");
  });
});
