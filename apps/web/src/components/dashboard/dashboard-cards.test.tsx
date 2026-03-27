import React from "react";
import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { OnboardingStatusCard } from "@/components/dashboard/onboarding-status-card";
import { RecommendationBoard } from "@/components/dashboard/recommendation-board";
import type { DashboardOnboardingState } from "@/lib/dashboard_onboarding";

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

function buildOnboardingState(
  overrides?: Partial<DashboardOnboardingState>,
): DashboardOnboardingState {
  return {
    isComplete: false,
    completionLabel: "1/3 입력",
    completedCount: 1,
    requiredCount: 3,
    missingFields: ["must_haves", "deal_breakers"],
    fields: [
      {
        key: "role",
        label: "목표 직무",
        detail: "ML Engineer",
        isComplete: true,
        statusLabel: "입력됨",
      },
      {
        key: "must_haves",
        label: "필수 조건",
        detail: "아직 입력되지 않음",
        isComplete: false,
        statusLabel: "미입력",
      },
      {
        key: "deal_breakers",
        label: "비선호 조건",
        detail: "아직 입력되지 않음",
        isComplete: false,
        statusLabel: "미입력",
      },
    ],
    role: "ML Engineer",
    yearsOfExperience: 6,
    mustHaves: [],
    dealBreakers: [],
    minimumFitScore: 85,
    ...overrides,
  };
}

describe("OnboardingStatusCard", () => {
  it("renders a checklist for incomplete onboarding and makes the whole card clickable", () => {
    render(<OnboardingStatusCard state={buildOnboardingState()} />);

    expect(screen.getByText("추천 기준이 아직 부족합니다")).toBeInTheDocument();
    expect(screen.getByText("목표 직무")).toBeInTheDocument();
    expect(screen.getByText("필수 조건")).toBeInTheDocument();
    expect(screen.getByText("비선호 조건")).toBeInTheDocument();
    expect(screen.getByText("1/3 입력")).toBeInTheDocument();
    expect(screen.getAllByText("아직 입력되지 않음")).toHaveLength(2);
    expect(screen.queryByText(/^온보딩$/)).not.toBeInTheDocument();
    expect(screen.getByRole("link", { name: "온보딩 설정 열기" })).toHaveAttribute(
      "href",
      "/onboarding",
    );
  });

  it("renders a calm summary card once onboarding is complete", () => {
    render(
      <OnboardingStatusCard
        state={buildOnboardingState({
          isComplete: true,
          completionLabel: "3/3 입력",
          completedCount: 3,
          missingFields: [],
          fields: [
            {
              key: "role",
              label: "목표 직무",
              detail: "ML Engineer",
              isComplete: true,
              statusLabel: "입력됨",
            },
            {
              key: "must_haves",
              label: "필수 조건",
              detail: "4개 입력됨",
              isComplete: true,
              statusLabel: "입력됨",
            },
            {
              key: "deal_breakers",
              label: "비선호 조건",
              detail: "1개 입력됨",
              isComplete: true,
              statusLabel: "입력됨",
            },
          ],
          mustHaves: ["Python", "LLM", "MLOps", "Remote"],
          dealBreakers: ["Onsite"],
        })}
      />,
    );

    expect(screen.getByText("ML Engineer")).toBeInTheDocument();
    expect(screen.getByText("Python")).toBeInTheDocument();
    expect(screen.getByText("LLM")).toBeInTheDocument();
    expect(screen.getByText("MLOps")).toBeInTheDocument();
    expect(screen.getByText("+1")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "온보딩 설정 수정" })).toHaveAttribute(
      "href",
      "/onboarding",
    );
  });
});

describe("RecommendationBoard", () => {
  it("renders the empty state when there are no recommendations", () => {
    render(<RecommendationBoard minimumFitScore={80} recommendations={[]} />);

    expect(screen.getByText("아직 비어 있습니다")).toBeInTheDocument();
    expect(screen.getByText("기준 80+")).toBeInTheDocument();
  });

  it("renders compact recommendation cards with feedback and links", () => {
    render(
      <RecommendationBoard
        minimumFitScore={85}
        recommendations={[
          {
            evaluationId: "eval-1",
            status: "LLM_EVALUATED",
            statusLabel: "평가 완료",
            fitScore: 92,
            reasoning: "LLM 평가에서 높은 적합도로 분류됐습니다.",
            userFeedback: "LIKE",
            feedbackLabel: "좋아요",
            feedbackReason: null,
            title: "Senior ML Engineer",
            company: "OpenAI",
            url: "https://example.com/jobs/1",
            platform: "LinkedIn",
          },
        ]}
      />,
    );

    expect(screen.getByText("Senior ML Engineer")).toBeInTheDocument();
    expect(screen.getByText("평가 완료")).toBeInTheDocument();
    expect(screen.getByText("피드백 좋아요")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "공고 보기" })).toHaveAttribute(
      "href",
      "https://example.com/jobs/1",
    );
  });
});
