import React from "react";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";

import { OnboardingMockup } from "@/components/profile/onboarding-mockup";

describe("OnboardingMockup", () => {
  it("renders the choice-based onboarding prototype and updates the preview", async () => {
    const user = userEvent.setup();

    render(<OnboardingMockup />);

    expect(
      screen.getByRole("heading", { name: "텍스트 대신 선택으로 기준을 빠르게 맞춥니다" }),
    ).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "Data Scientist" }));
    await user.type(
      screen.getByPlaceholderText("직접 스킬 키워드 추가, 예: Spark, 추천 시스템, LangChain"),
      "Feature Store",
    );
    await user.click(screen.getAllByRole("button", { name: "추가" })[1]);
    await user.click(screen.getAllByText("고급 설정")[1]);

    expect(screen.getByText(/ML Engineer, LLM Engineer, Data Scientist/)).toBeInTheDocument();
    expect(screen.getAllByText(/Feature Store/).length).toBeGreaterThan(0);
    expect(screen.getAllByRole("button", { name: /강하게 왼쪽/ }).length).toBeGreaterThan(0);
    expect(screen.getByText("Front-end mock only")).toBeInTheDocument();
  });
});
