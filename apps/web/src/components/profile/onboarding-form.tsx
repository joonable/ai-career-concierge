"use client";

import React, { startTransition, useState } from "react";

import { updateProfile } from "@/lib/api_client_browser";
import {
  mapOnboardingFormStateToProfilePayload,
  type OnboardingFormState,
} from "@/lib/profile_types";

type OnboardingFormProps = {
  initialProfile: OnboardingFormState;
};

type StatusTone = "neutral" | "success" | "error";

export function OnboardingForm({ initialProfile }: OnboardingFormProps) {
  const [state, setState] = useState(initialProfile);
  const [isPending, setIsPending] = useState(false);
  const [status, setStatus] = useState({
    tone: "neutral" as StatusTone,
    message: "저장하면 대시보드와 평가 파이프라인에 바로 반영됩니다.",
  });

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setIsPending(true);
    setStatus({
      tone: "neutral",
      message: "저장 요청을 전송하고 있습니다.",
    });

    startTransition(async () => {
      try {
        await updateProfile(mapOnboardingFormStateToProfilePayload(state));
        setStatus({
          tone: "success",
          message: "프로필을 저장했습니다. 대시보드로 이동합니다.",
        });
        window.location.href = "/dashboard";
      } catch (error) {
        setStatus({
          tone: "error",
          message: `저장 실패: ${error instanceof Error ? error.message : "프로필을 저장하지 못했습니다."}`,
        });
      } finally {
        setIsPending(false);
      }
    });
  };

  return (
    <section className="dashboard-card onboarding-form-card">
      <div className="onboarding-form__header">
        <div className="dashboard-summary-card__copy">
          <span className="dashboard-kicker">Profile Settings</span>
          <h2 className="dashboard-section__title">기준 입력</h2>
        </div>
        <span className="dashboard-pill">SLACK</span>
      </div>
      <form className="onboarding-form" onSubmit={handleSubmit}>
        <div className="onboarding-form__grid">
          <label className="onboarding-field">
            <span>목표 직무</span>
            <input
              className="onboarding-field__input"
              name="role"
              placeholder="예: Machine Learning Engineer"
              onChange={(event) => setState((current) => ({ ...current, role: event.target.value }))}
              value={state.role}
            />
          </label>
          <label className="onboarding-field">
            <span>총 경력 연차</span>
            <input
              className="onboarding-field__input"
              inputMode="numeric"
              name="yearsOfExperience"
              placeholder="0"
              onChange={(event) =>
                setState((current) => ({ ...current, yearsOfExperience: event.target.value }))
              }
              value={state.yearsOfExperience}
            />
          </label>
          <label className="onboarding-field onboarding-field--wide">
            <span>필수 조건</span>
            <textarea
              className="onboarding-field__input onboarding-field__textarea"
              name="mustHaves"
              placeholder="예: Python, SQL, recommender systems"
              onChange={(event) =>
                setState((current) => ({ ...current, mustHaves: event.target.value }))
              }
              value={state.mustHaves}
            />
          </label>
          <label className="onboarding-field onboarding-field--wide">
            <span>비선호 조건</span>
            <textarea
              className="onboarding-field__input onboarding-field__textarea"
              name="dealBreakers"
              placeholder="예: contract-only, pure frontend"
              onChange={(event) =>
                setState((current) => ({ ...current, dealBreakers: event.target.value }))
              }
              value={state.dealBreakers}
            />
          </label>
          <label className="onboarding-field onboarding-field--wide">
            <span>최소 적합도 점수</span>
            <input
              className="onboarding-field__input"
              inputMode="numeric"
              name="minimumFitScore"
              placeholder="80"
              onChange={(event) =>
                setState((current) => ({ ...current, minimumFitScore: event.target.value }))
              }
              value={state.minimumFitScore}
            />
          </label>
        </div>
        <div className="onboarding-form__footer">
          <button className="onboarding-submit" disabled={isPending} type="submit">
            {isPending ? "저장 중..." : "저장 후 대시보드로"}
          </button>
          <p
            className={[
              "onboarding-status",
              `onboarding-status--${status.tone}`,
            ].join(" ")}
          >
            {status.message}
          </p>
        </div>
      </form>
    </section>
  );
}
