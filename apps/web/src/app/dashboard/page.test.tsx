import React from "react";
import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import DashboardPage from "@/app/dashboard/page";

const getDashboardSnapshot = vi.fn();
const getProfileSnapshot = vi.fn();

vi.mock("next/link", () => ({
  default: ({
    children,
    href,
    ...props
  }: React.AnchorHTMLAttributes<HTMLAnchorElement> & { href: string }) => (
    <a href={href} {...props}>
      {children}
    </a>
  ),
}));

vi.mock("@/lib/api_client_server", () => ({
  getDashboardSnapshot: (...args: unknown[]) => getDashboardSnapshot(...args),
  getProfileSnapshot: (...args: unknown[]) => getProfileSnapshot(...args),
}));

describe("DashboardPage", () => {
  beforeEach(() => {
    getDashboardSnapshot.mockReset();
    getProfileSnapshot.mockReset();
  });

  it("uses the stricter onboarding completion rule in the hero copy and stats", async () => {
    getDashboardSnapshot.mockResolvedValue({
      user_id: "user-1",
      minimum_fit_score: 82,
      recommendations: [],
    });
    getProfileSnapshot.mockResolvedValue({
      user_id: "user-1",
      email: "scaffold-user@example.com",
      profile_data: {
        role: "ML Engineer",
        years_of_experience: 6,
        title_keywords: [],
      },
      guidelines: {
        must_haves: [],
        deal_breakers: [],
      },
      notification_settings: {
        minimum_fit_score: 82,
        delivery_channel: "slack",
      },
    });

    render(await DashboardPage());

    expect(
      screen.getByText("추천 기준 1/3 입력. 남은 항목을 채우면 더 정확한 추천을 받을 수 있습니다."),
    ).toBeInTheDocument();
    expect(screen.getAllByText("1/3 입력")).toHaveLength(2);
  });
});
