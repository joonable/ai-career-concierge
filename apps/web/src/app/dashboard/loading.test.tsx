import React from "react";
import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import DashboardLoading from "@/app/dashboard/loading";

describe("DashboardLoading", () => {
  it("renders an accessible loading state for the dashboard route", () => {
    render(<DashboardLoading />);

    expect(screen.getByText("대시보드를 불러오는 중입니다.")).toBeInTheDocument();
    expect(screen.getByRole("main")).toHaveAttribute("aria-busy", "true");
  });
});
