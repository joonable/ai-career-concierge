import React from "react";
import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import DashboardPage from "@/app/dashboard/page";

const loadDashboardPageData = vi.fn();

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

vi.mock("@/lib/dashboard_loader", () => ({
  loadDashboardPageData: (...args: unknown[]) => loadDashboardPageData(...args),
}));

describe("DashboardPage", () => {
  beforeEach(() => {
    loadDashboardPageData.mockReset();
  });

  it("uses the stricter onboarding completion rule in the hero copy and stats", async () => {
    loadDashboardPageData.mockResolvedValue({
      status: "ready",
      dashboard: {
        user_id: "user-1",
        minimum_fit_score: 82,
        recommendations: [],
      },
      profile: {
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
      },
    });

    render(await DashboardPage());

    expect(
      screen.getByText("추천 기준 1/3 입력. 남은 항목을 채우면 더 정확한 추천을 받을 수 있습니다."),
    ).toBeInTheDocument();
    expect(screen.getAllByText("1/3 입력")).toHaveLength(2);
  });

  it("renders the dashboard empty state from an empty API response", async () => {
    loadDashboardPageData.mockResolvedValue({
      status: "ready",
      dashboard: {
        user_id: "user-1",
        minimum_fit_score: 80,
        recommendations: [],
      },
      profile: {
        user_id: "user-1",
        email: "scaffold-user@example.com",
        profile_data: {
          role: "Machine Learning Engineer",
          years_of_experience: 6,
          title_keywords: ["machine learning"],
        },
        guidelines: {
          must_haves: ["Python"],
          deal_breakers: ["contract-only"],
        },
        notification_settings: {
          minimum_fit_score: 80,
          delivery_channel: "slack",
        },
      },
    });

    render(await DashboardPage());

    expect(screen.getByText("아직 비어 있습니다")).toBeInTheDocument();
    expect(screen.getByText("파이프라인 실행 후 여기에 표시됩니다.")).toBeInTheDocument();
  });

  it("renders an in-page error state when dashboard data loading fails", async () => {
    loadDashboardPageData.mockResolvedValue({
      status: "error",
      message: "추천 대시보드를 불러오지 못했습니다.",
    });

    render(await DashboardPage());

    expect(screen.getByText("대시보드를 불러오지 못했습니다")).toBeInTheDocument();
    expect(screen.getByText("추천 대시보드를 불러오지 못했습니다.")).toBeInTheDocument();
  });
});
