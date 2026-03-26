import { LoginCard } from "@/components/auth/login-card";

export default function LoginPage() {
  return (
    <main>
      <div className="shell hero">
        <section className="stack">
          <span className="eyebrow">Precision-first job matching</span>
          <h1 className="display">Let the noisy feed burn off before it reaches you.</h1>
          <p className="lead">
            This PoC filters job listings through rules, LLM evaluation, Slack delivery,
            and feedback memory. The first version is built for one primary user and one
            reliable loop.
          </p>
        </section>
        <LoginCard />
      </div>
    </main>
  );
}
