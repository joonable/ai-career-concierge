"use client";

import { startTransition, useState } from "react";

import { updateProfile } from "@/lib/api_client";

const INITIAL_STATE = {
  role: "Machine Learning Engineer",
  yearsOfExperience: "6",
  mustHaves: "Python, SQL, recommender systems",
  dealBreakers: "contract-only, pure frontend",
  minimumFitScore: "80",
};

export function OnboardingForm() {
  const [state, setState] = useState(INITIAL_STATE);
  const [isPending, setIsPending] = useState(false);
  const [status, setStatus] = useState("Submit once to persist profile defaults in FastAPI.");

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setIsPending(true);
    startTransition(async () => {
      try {
        await updateProfile({
          profile_data: {
            role: state.role,
            years_of_experience: Number(state.yearsOfExperience),
            title_keywords: ["machine learning", "ml", "ai"],
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
        setStatus("Profile saved. Opening the dashboard.");
        window.location.href = "/dashboard";
      } catch {
        setStatus("Backend unreachable. The UI scaffold is still in place and ready to wire.");
      } finally {
        setIsPending(false);
      }
    });
  };

  return (
    <section className="panel" style={{ padding: 28 }}>
      <form className="form" onSubmit={handleSubmit}>
        <label className="field">
          <span>Target role</span>
          <input
            name="role"
            onChange={(event) => setState((current) => ({ ...current, role: event.target.value }))}
            value={state.role}
          />
        </label>
        <label className="field">
          <span>Years of experience</span>
          <input
            inputMode="numeric"
            name="yearsOfExperience"
            onChange={(event) =>
              setState((current) => ({ ...current, yearsOfExperience: event.target.value }))
            }
            value={state.yearsOfExperience}
          />
        </label>
        <label className="field">
          <span>Must-haves</span>
          <textarea
            name="mustHaves"
            onChange={(event) => setState((current) => ({ ...current, mustHaves: event.target.value }))}
            value={state.mustHaves}
          />
        </label>
        <label className="field">
          <span>Deal-breakers</span>
          <textarea
            name="dealBreakers"
            onChange={(event) =>
              setState((current) => ({ ...current, dealBreakers: event.target.value }))
            }
            value={state.dealBreakers}
          />
        </label>
        <label className="field">
          <span>Minimum fit score</span>
          <input
            inputMode="numeric"
            name="minimumFitScore"
            onChange={(event) =>
              setState((current) => ({ ...current, minimumFitScore: event.target.value }))
            }
            value={state.minimumFitScore}
          />
        </label>
        <button className="button primary" disabled={isPending} type="submit">
          {isPending ? "Saving..." : "Save profile"}
        </button>
        <p className="muted" style={{ margin: 0 }}>{status}</p>
      </form>
    </section>
  );
}
