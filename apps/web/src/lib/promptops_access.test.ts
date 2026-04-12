import { beforeEach, describe, expect, it, vi } from "vitest";

import { ensurePromptOpsAdminAccess, isPromptOpsAdminEmail } from "@/lib/promptops_access";

const getSession = vi.fn();
const notFound = vi.fn(() => {
  throw new Error("NEXT_NOT_FOUND");
});

vi.mock("next/navigation", () => ({
  notFound: () => notFound(),
}));

vi.mock("@/lib/supabase_auth_server", () => ({
  createSupabaseServerClient: async () => ({
    auth: {
      getSession,
    },
  }),
}));

describe("promptops access", () => {
  const originalEnv = process.env.PROMPTOPS_ADMIN_EMAILS;
  const originalBypass = process.env.PROMPTOPS_DEV_BYPASS;

  beforeEach(() => {
    getSession.mockReset();
    notFound.mockClear();
    process.env.PROMPTOPS_ADMIN_EMAILS = originalEnv;
    process.env.PROMPTOPS_DEV_BYPASS = originalBypass;
    vi.unstubAllEnvs();
  });

  it("normalizes env allowlist entries", () => {
    process.env.PROMPTOPS_ADMIN_EMAILS = "Admin@example.com, admin@example.com, second@example.com";

    expect(isPromptOpsAdminEmail("admin@example.com")).toBe(true);
    expect(isPromptOpsAdminEmail("SECOND@example.com")).toBe(true);
    expect(isPromptOpsAdminEmail("other@example.com")).toBe(false);
  });

  it("rejects access when env allowlist is missing", async () => {
    delete process.env.PROMPTOPS_ADMIN_EMAILS;

    await expect(ensurePromptOpsAdminAccess()).rejects.toThrow("NEXT_NOT_FOUND");
  });

  it("allows configured admin emails", async () => {
    process.env.PROMPTOPS_ADMIN_EMAILS = "scaffold-user@example.com";
    getSession.mockResolvedValue({
      data: {
        session: {
          user: {
            email: "scaffold-user@example.com",
          },
        },
      },
    });

    await expect(ensurePromptOpsAdminAccess()).resolves.toBeUndefined();
  });

  it("allows local development bypass when explicitly enabled", async () => {
    delete process.env.PROMPTOPS_ADMIN_EMAILS;
    process.env.PROMPTOPS_DEV_BYPASS = "true";
    vi.stubEnv("NODE_ENV", "development");

    await expect(ensurePromptOpsAdminAccess()).resolves.toBeUndefined();
  });

  it("rejects non-admin emails", async () => {
    process.env.PROMPTOPS_ADMIN_EMAILS = "scaffold-user@example.com";
    getSession.mockResolvedValue({
      data: {
        session: {
          user: {
            email: "other-user@example.com",
          },
        },
      },
    });

    await expect(ensurePromptOpsAdminAccess()).rejects.toThrow("NEXT_NOT_FOUND");
  });
});
