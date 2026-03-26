import { OnboardingForm } from "@/components/profile/onboarding-form";

export default function OnboardingPage() {
  return (
    <main>
      <div className="shell stack">
        <section className="hero">
          <div className="stack">
            <span className="eyebrow">Onboarding</span>
            <h1 className="display">Tune the rules before the model ever gets involved.</h1>
            <p className="lead">
              Capture role, seniority, must-haves, deal-breakers, and the default delivery
              threshold. The backend stores these as profile, guideline, and notification
              settings for the pipeline.
            </p>
          </div>
        </section>
        <OnboardingForm />
      </div>
    </main>
  );
}
