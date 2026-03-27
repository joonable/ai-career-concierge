"use client";

import { startTransition, useState } from "react";

import { updateProfile } from "@/lib/api_client_browser";
import type { OnboardingFormState } from "@/lib/profile_types";

type OnboardingFormProps = {
  initialProfile: OnboardingFormState;
};

export function OnboardingForm({ initialProfile }: OnboardingFormProps) {
  const [state, setState] = useState(initialProfile);
  const [isPending, setIsPending] = useState(false);
  const [status, setStatus] = useState("한 번 저장하면 FastAPI에 기본 프로필 설정이 반영됩니다.");

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setIsPending(true);
    startTransition(async () => {
      try {
        await updateProfile({
          profile_data: {
            role: state.role,
            years_of_experience: Number(state.yearsOfExperience),
            title_keywords: [],
          },
          guidelines: {
            must_haves: state.mustHaves.split(",").map((item) => item.trim()).filter(Boolean),
            deal_breakers: state.dealBreakers.split(",").map((item) => item.trim()).filter(Boolean),
          },
          notification_settings: {
            minimum_fit_score: Number(state.minimumFitScore),
            delivery_channel: "slack",
          },
        });
        setStatus("프로필을 저장했습니다. 대시보드로 이동합니다.");
        window.location.href = "/dashboard";
      } catch {
        setStatus("백엔드에 연결할 수 없습니다. UI 뼈대는 유지되어 있으며 연동만 남아 있습니다.");
      } finally {
        setIsPending(false);
      }
    });
  };

  return (
    <section className="panel" style={{ padding: 28 }}>
      <form className="form" onSubmit={handleSubmit}>
        <label className="field">
          <span>목표 직무</span>
          <input
            name="role"
            placeholder="예: Machine Learning Engineer"
            onChange={(event) => setState((current) => ({ ...current, role: event.target.value }))}
            value={state.role}
          />
        </label>
        <label className="field">
          <span>총 경력 연차</span>
          <input
            inputMode="numeric"
            name="yearsOfExperience"
            placeholder="0"
            onChange={(event) =>
              setState((current) => ({ ...current, yearsOfExperience: event.target.value }))
            }
            value={state.yearsOfExperience}
          />
        </label>
        <label className="field">
          <span>필수 조건</span>
          <textarea
            name="mustHaves"
            placeholder="예: Python, SQL, recommender systems"
            onChange={(event) => setState((current) => ({ ...current, mustHaves: event.target.value }))}
            value={state.mustHaves}
          />
        </label>
        <label className="field">
          <span>비선호 조건</span>
          <textarea
            name="dealBreakers"
            placeholder="예: contract-only, pure frontend"
            onChange={(event) =>
              setState((current) => ({ ...current, dealBreakers: event.target.value }))
            }
            value={state.dealBreakers}
          />
        </label>
        <label className="field">
          <span>최소 적합도 점수</span>
          <input
            inputMode="numeric"
            name="minimumFitScore"
            placeholder="80"
            onChange={(event) =>
              setState((current) => ({ ...current, minimumFitScore: event.target.value }))
            }
            value={state.minimumFitScore}
          />
        </label>
        <button className="button primary" disabled={isPending} type="submit">
          {isPending ? "저장 중..." : "프로필 저장"}
        </button>
        <p className="muted" style={{ margin: 0 }}>{status}</p>
      </form>
    </section>
  );
}
