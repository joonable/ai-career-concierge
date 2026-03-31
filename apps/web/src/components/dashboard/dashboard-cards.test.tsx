import React from "react";
import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { OnboardingStatusCard } from "@/components/dashboard/onboarding-status-card";
import { RecommendationBoard } from "@/components/dashboard/recommendation-board";
import type { DashboardOnboardingState } from "@/lib/dashboard_onboarding";
import type { DashboardRecommendation } from "@/lib/dashboard_mapper";
import type { UserProfileResponse } from "@/lib/profile_types";

const recordEvaluationFeedback = vi.fn();

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

vi.mock("@/lib/api_client_browser", () => ({
  recordEvaluationFeedback: (...args: unknown[]) => recordEvaluationFeedback(...args),
}));

function buildOnboardingState(
  overrides?: Partial<DashboardOnboardingState>,
): DashboardOnboardingState {
  return {
    isComplete: false,
    completionLabel: "1/3 입력",
    completedCount: 1,
    requiredCount: 3,
    missingFields: ["skills", "exclusions"],
    fields: [
      {
        key: "role",
        label: "목표 직무",
        detail: "ML Engineer",
        isComplete: true,
        statusLabel: "입력됨",
      },
      {
        key: "skills",
        label: "중요 스킬",
        detail: "아직 입력되지 않음",
        isComplete: false,
        statusLabel: "미입력",
      },
      {
        key: "exclusions",
        label: "제외 조건",
        detail: "아직 입력되지 않음",
        isComplete: false,
        statusLabel: "미입력",
      },
    ],
    role: "ML Engineer",
    yearsOfExperience: 6,
    preferredSkills: [],
    exclusions: [],
    workModes: [],
    locations: [],
    teamContexts: [],
    minimumFitScore: 85,
    ...overrides,
  };
}

function buildRecommendation(overrides: Partial<DashboardRecommendation> = {}): DashboardRecommendation {
  const recommendation: DashboardRecommendation = {
    evaluationId: "eval-1",
    status: "LLM_EVALUATED",
    statusLabel: "평가 완료",
    fitScore: 92,
    reasoning: "LLM 평가에서 높은 적합도로 분류됐습니다.",
    decisionSummary: "적합도 92점으로 추천 기준을 충족했습니다.",
    matchHighlights: ["필수 조건 일치: Python", "직무 키워드가 공고 제목과 일치합니다."],
    riskHighlights: ["JD에 구조화된 요구사항이 부족해 사람이 한 번 더 확인하는 편이 안전합니다."],
    confidenceLevel: "HIGH",
    ruleRejectionReason: null,
    ruleMatchReasons: ["목표 직무 'ML Engineer' 기준에서 공고 제목이 관련 키워드와 일치합니다."],
    ruleRejectionDetails: [],
    userFeedback: "LIKE",
    feedbackLabel: "좋아요",
    feedbackReason: null,
    createdAt: "2026-03-30T09:00:00+09:00",
    updatedAt: "2026-03-30T09:10:00+09:00",
    title: "Senior ML Engineer",
    company: "OpenAI",
    url: "https://example.com/jobs/1",
    platform: "LinkedIn",
    jdRawText: "Python SQL MLOps recommender systems ownership in Seoul.",
    minYearsExperience: 5,
    maxYearsExperience: 8,
    sourceMetadata: {
      location: "Seoul",
      employment_type: "Full-time",
    },
    responsibilities: ["Production ML systems ownership", "Platform improvement"],
    requirements: ["Python experience", "SQL experience"],
    preferredRequirements: ["MLOps experience"],
    location: "Seoul",
    employmentType: "Full-time",
  };

  return { ...recommendation, ...overrides };
}

function buildProfile(overrides?: Partial<UserProfileResponse>): UserProfileResponse {
  return {
    user_id: "user-1",
    email: "scaffold-user@example.com",
    profile_data: {
      role: "ML Engineer",
      years_of_experience: 6,
      title_keywords: ["ml engineer"],
    },
    guidelines: {
      must_haves: ["Python", "SQL", "MLOps"],
      deal_breakers: ["contract-only", "onsite-only"],
    },
    preferences: {
      work_modes: [],
      locations: [],
      team_contexts: [],
      skills: { preset: ["python", "sql", "mlops"], custom: [] },
      exclusions: { preset: ["contract", "onsite-only"], custom: [] },
      comparisons: {},
      note: null,
    },
    notification_settings: {
      minimum_fit_score: 85,
      delivery_channel: "slack",
    },
    ...overrides,
  };
}

describe("OnboardingStatusCard", () => {
  it("renders a checklist for incomplete onboarding and makes the whole card clickable", () => {
    render(<OnboardingStatusCard state={buildOnboardingState()} />);

    expect(screen.getByText("추천 기준이 아직 부족합니다")).toBeInTheDocument();
    expect(screen.getByText("목표 직무")).toBeInTheDocument();
    expect(screen.getByText("중요 스킬")).toBeInTheDocument();
    expect(screen.getByText("제외 조건")).toBeInTheDocument();
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
              key: "skills",
              label: "중요 스킬",
              detail: "4개 입력됨",
              isComplete: true,
              statusLabel: "입력됨",
            },
            {
              key: "exclusions",
              label: "제외 조건",
              detail: "1개 입력됨",
              isComplete: true,
              statusLabel: "입력됨",
            },
          ],
          preferredSkills: ["Python", "LLM", "MLOps", "Remote"],
          exclusions: ["Onsite"],
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
  beforeEach(() => {
    recordEvaluationFeedback.mockReset();
    recordEvaluationFeedback.mockResolvedValue({
      evaluation_id: "eval-1",
      feedback: "LIKE",
      feedback_reason: null,
    });
  });

  it("renders the empty state when there are no recommendations", () => {
    render(<RecommendationBoard minimumFitScore={80} profile={buildProfile()} recommendations={[]} />);

    expect(screen.getByText("아직 비어 있습니다")).toBeInTheDocument();
    expect(screen.getByText("기준 80+ 추천 중심")).toBeInTheDocument();
  });

  it("renders friendly filters and recommendation cards", () => {
    render(
      <RecommendationBoard
        minimumFitScore={85}
        profile={buildProfile()}
        recommendations={[buildRecommendation()]}
      />,
    );

    expect(screen.getByPlaceholderText("회사명이나 직무명으로 찾기")).toBeInTheDocument();
    expect(screen.getAllByRole("button", { name: "전체" }).length).toBeGreaterThan(0);
    expect(screen.getByRole("button", { name: "추천만" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "검토필요" })).toBeInTheDocument();
    expect(screen.getByText("추천 기준 85점 이상만 보기")).toBeInTheDocument();
    expect(screen.getByText("규칙에서 제외된 공고도 포함")).toBeInTheDocument();
    expect(screen.getByText("기준 충족")).toBeInTheDocument();
    expect(screen.getByText("피드백 좋아요")).toBeInTheDocument();
  });

  it("reveals pending recommendations when the score checkbox is turned off", async () => {
    const user = userEvent.setup();

    render(
      <RecommendationBoard
        minimumFitScore={85}
        profile={buildProfile()}
        recommendations={[
          buildRecommendation({
            evaluationId: "eval-2",
            status: "PENDING",
            statusLabel: "대기",
            fitScore: null,
            reasoning: null,
            userFeedback: null,
            feedbackLabel: null,
            title: "Platform Engineer",
            company: "Signal Labs",
            url: "https://example.com/jobs/2",
          }),
        ]}
      />,
    );

    expect(screen.getByText("현재 필터와 일치하는 공고가 없습니다")).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "검토필요" }));

    expect(screen.getByText("Platform Engineer")).toBeInTheDocument();
    expect(screen.getAllByText("대기")).toHaveLength(2);
    expect(screen.getByText("피드백 대기")).toBeInTheDocument();
  });

  it("includes rejected jobs and highlights the rejection reason when enabled", async () => {
    const user = userEvent.setup();

    render(
      <RecommendationBoard
        minimumFitScore={85}
        profile={buildProfile()}
        recommendations={[
          buildRecommendation(),
          buildRecommendation({
            evaluationId: "eval-3",
            status: "RULE_REJECTED",
            statusLabel: "규칙 제외",
            fitScore: null,
            reasoning: null,
            ruleRejectionReason: "TITLE_MISMATCH",
            userFeedback: null,
            feedbackLabel: null,
            title: "Junior Analyst",
            url: "https://example.com/jobs/3",
          }),
        ]}
      />,
    );

    expect(screen.queryByText("Junior Analyst")).not.toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "검토필요" }));
    await user.click(screen.getByLabelText("규칙에서 제외된 공고도 포함"));

    expect(screen.getByText("Junior Analyst")).toBeInTheDocument();
    expect(screen.getByText("제외 사유 Title Mismatch")).toBeInTheDocument();
  });

  it("supports search, feedback filter, and platform filter together", async () => {
    const user = userEvent.setup();

    render(
      <RecommendationBoard
        minimumFitScore={70}
        profile={buildProfile()}
        recommendations={[
          buildRecommendation({
            evaluationId: "eval-1",
            title: "Senior ML Engineer",
            company: "OpenAI",
            platform: "LinkedIn",
            userFeedback: "LIKE",
            feedbackLabel: "좋아요",
          }),
          buildRecommendation({
            evaluationId: "eval-2",
            title: "MLOps Engineer",
            company: "Signal Labs",
            platform: "Wanted",
            userFeedback: null,
            feedbackLabel: null,
          }),
        ]}
      />,
    );

    await user.click(screen.getByRole("button", { name: "미응답" }));
    await user.click(screen.getByRole("button", { name: "Wanted" }));
    await user.type(screen.getByLabelText("공고 검색"), "Signal");

    expect(screen.getByText("MLOps Engineer")).toBeInTheDocument();
    expect(screen.queryByText("Senior ML Engineer")).not.toBeInTheDocument();
  });

  it("sorts recommendations by fit score when selected", async () => {
    const user = userEvent.setup();

    render(
      <RecommendationBoard
        minimumFitScore={80}
        profile={buildProfile()}
        recommendations={[
          buildRecommendation({
            evaluationId: "eval-1",
            title: "Mid ML Engineer",
            fitScore: 88,
            createdAt: "2026-03-30T08:00:00+09:00",
          }),
          buildRecommendation({
            evaluationId: "eval-2",
            title: "Senior ML Engineer",
            fitScore: 97,
            createdAt: "2026-03-29T08:00:00+09:00",
          }),
        ]}
      />,
    );

    await user.selectOptions(screen.getByLabelText("공고 정렬 기준"), "fit_desc");

    const titles = screen.getAllByRole("heading", { level: 3 }).map((node) => node.textContent);
    expect(titles.indexOf("Senior ML Engineer")).toBeLessThan(titles.indexOf("Mid ML Engineer"));
  });

  it("shows the review preset for jobs that need a human check", async () => {
    const user = userEvent.setup();

    render(
      <RecommendationBoard
        minimumFitScore={85}
        profile={buildProfile()}
        recommendations={[
          buildRecommendation({
            evaluationId: "eval-1",
            title: "Recommended Role",
            fitScore: 92,
            userFeedback: "LIKE",
            feedbackLabel: "좋아요",
          }),
          buildRecommendation({
            evaluationId: "eval-2",
            title: "Needs Review Role",
            fitScore: 78,
            userFeedback: null,
            feedbackLabel: null,
          }),
        ]}
      />,
    );

    await user.click(screen.getByRole("button", { name: "검토필요" }));

    expect(screen.getByText("Needs Review Role")).toBeInTheDocument();
    expect(screen.queryByText("Recommended Role")).not.toBeInTheDocument();
  });

  it("opens a centered detail modal with structured explanation when a card is clicked", async () => {
    const user = userEvent.setup();

    render(
      <RecommendationBoard
        minimumFitScore={85}
        profile={buildProfile()}
        recommendations={[buildRecommendation()]}
      />,
    );

    await user.click(screen.getByRole("button", { name: "Senior ML Engineer 상세 보기" }));

    expect(screen.getByRole("dialog", { name: "공고 상세 패널" })).toBeInTheDocument();
    expect(screen.getByText("피드백 저장")).toBeInTheDocument();
    expect(screen.getByText("매칭 근거")).toBeInTheDocument();
    expect(screen.getByText("리스크와 경고")).toBeInTheDocument();
    expect(screen.getByText("JD 핵심")).toBeInTheDocument();
    expect(screen.getByText("내 기준과 비교")).toBeInTheDocument();
    expect(screen.getByText("원문 공고 보기")).toHaveAttribute("href", "https://example.com/jobs/1");
  });

  it("closes the detail modal on escape and backdrop click", async () => {
    const user = userEvent.setup();

    render(
      <RecommendationBoard
        minimumFitScore={85}
        profile={buildProfile()}
        recommendations={[buildRecommendation()]}
      />,
    );

    await user.click(screen.getByRole("button", { name: "Senior ML Engineer 상세 보기" }));
    expect(screen.getByRole("dialog", { name: "공고 상세 패널" })).toBeInTheDocument();

    await user.keyboard("{Escape}");
    expect(screen.queryByRole("dialog", { name: "공고 상세 패널" })).not.toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "Senior ML Engineer 상세 보기" }));
    await user.click(screen.getByRole("dialog", { name: "공고 상세 패널" }));
    expect(screen.queryByRole("dialog", { name: "공고 상세 패널" })).not.toBeInTheDocument();
  });

  it("saves feedback actions from the detail panel", async () => {
    const user = userEvent.setup();
    recordEvaluationFeedback.mockResolvedValue({
      evaluation_id: "eval-1",
      feedback: "LATER",
      feedback_reason: "next week",
    });

    render(
      <RecommendationBoard
        minimumFitScore={85}
        profile={buildProfile()}
        recommendations={[buildRecommendation()]}
      />,
    );

    await user.click(screen.getByRole("button", { name: "Senior ML Engineer 상세 보기" }));
    const dialog = screen.getByRole("dialog", { name: "공고 상세 패널" });
    await user.click(within(dialog).getByRole("button", { name: "나중에 보기" }));
    expect(
      screen.getByText("나중에 보기는 관심은 있지만 아직 판단 전인 공고를 분리해두는 용도입니다."),
    ).toBeInTheDocument();
    await user.type(screen.getByLabelText("피드백 메모"), "next week");
    await user.click(within(dialog).getByRole("button", { name: "나중에 보기 저장" }));

    expect(recordEvaluationFeedback).toHaveBeenCalledWith("eval-1", {
      feedback: "LATER",
      feedback_reason: "next week",
    });
    expect(screen.getByText("피드백이 저장되었습니다.")).toBeInTheDocument();
    expect(screen.getByText("피드백 나중에 보기")).toBeInTheDocument();
  });

  it("updates modal guidance when a different feedback action is selected", async () => {
    const user = userEvent.setup();

    render(
      <RecommendationBoard
        minimumFitScore={85}
        profile={buildProfile()}
        recommendations={[buildRecommendation({ userFeedback: null, feedbackLabel: null })]}
      />,
    );

    await user.click(screen.getByRole("button", { name: "Senior ML Engineer 상세 보기" }));
    const dialog = screen.getByRole("dialog", { name: "공고 상세 패널" });

    expect(within(dialog).getByRole("button", { name: "피드백 선택 후 저장" })).toBeDisabled();

    await user.click(within(dialog).getByRole("button", { name: "좋아요" }));
    expect(
      screen.getByText("좋아요는 이후 비슷한 공고를 더 자주 추천하는 데 도움이 됩니다."),
    ).toBeInTheDocument();
    expect(screen.getByLabelText("피드백 메모")).toHaveAttribute(
      "placeholder",
      "어떤 점이 특히 잘 맞는지 남겨보세요",
    );
    expect(within(dialog).getByRole("button", { name: "좋아요 저장" })).toBeEnabled();

    await user.click(within(dialog).getByRole("button", { name: "제외" }));
    expect(
      screen.getByText("싫어요는 단기 메모리에 반영되어 비슷한 공고를 줄이는 데 사용됩니다."),
    ).toBeInTheDocument();
    expect(screen.getByLabelText("피드백 메모")).toHaveAttribute(
      "placeholder",
      "왜 제외하려는지 간단히 남겨보세요",
    );
  });

  it("updates the current filtered list immediately after saving feedback", async () => {
    const user = userEvent.setup();
    recordEvaluationFeedback.mockResolvedValue({
      evaluation_id: "eval-2",
      feedback: "LATER",
      feedback_reason: "follow up later",
    });

    render(
      <RecommendationBoard
        minimumFitScore={70}
        profile={buildProfile()}
        recommendations={[
          buildRecommendation({
            evaluationId: "eval-1",
            title: "Saved Like Role",
            userFeedback: "LIKE",
            feedbackLabel: "좋아요",
          }),
          buildRecommendation({
            evaluationId: "eval-2",
            title: "Unsure Role",
            userFeedback: null,
            feedbackLabel: null,
          }),
        ]}
      />,
    );

    await user.click(screen.getByRole("button", { name: "미응답" }));
    expect(screen.getByText("Unsure Role")).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "Unsure Role 상세 보기" }));
    const dialog = screen.getByRole("dialog", { name: "공고 상세 패널" });
    await user.click(within(dialog).getByRole("button", { name: "나중에 보기" }));
    await user.type(screen.getByLabelText("피드백 메모"), "follow up later");
    await user.click(within(dialog).getByRole("button", { name: "나중에 보기 저장" }));

    expect(screen.queryByRole("button", { name: "Unsure Role 상세 보기" })).not.toBeInTheDocument();
    expect(screen.getByText("현재 필터와 일치하는 공고가 없습니다")).toBeInTheDocument();
  });

  it("lets the user save feedback directly from the dashboard card and reflects it immediately", async () => {
    const user = userEvent.setup();
    recordEvaluationFeedback.mockResolvedValue({
      evaluation_id: "eval-1",
      feedback: "DISLIKE",
      feedback_reason: "직접 검토 후 제외",
    });

    render(
      <RecommendationBoard
        minimumFitScore={70}
        profile={buildProfile()}
        recommendations={[buildRecommendation({ userFeedback: null, feedbackLabel: null })]}
      />,
    );

    const card = screen.getByRole("button", { name: "Senior ML Engineer 상세 보기" }).closest("article");
    expect(card).not.toBeNull();

    await user.click(within(card as HTMLElement).getByRole("button", { name: "싫어요" }));

    expect(recordEvaluationFeedback).toHaveBeenCalledWith("eval-1", {
      feedback: "DISLIKE",
      feedback_reason: "직접 검토 후 제외",
    });
    expect(screen.getByText("피드백 제외")).toBeInTheDocument();
    expect(screen.getByText("최근 메모: 직접 검토 후 제외")).toBeInTheDocument();
  });
});
