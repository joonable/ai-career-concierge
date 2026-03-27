import Link from "next/link";

type OnboardingSummary = {
  isComplete: boolean;
  role: string;
  yearsOfExperience: number;
  mustHaves: string[];
  dealBreakers: string[];
  minimumFitScore: number;
};

type OnboardingStatusCardProps = {
  summary: OnboardingSummary;
};

export function OnboardingStatusCard({ summary }: OnboardingStatusCardProps) {
  if (!summary.isComplete) {
    return (
      <section className="panel board-card">
        <div className="stack">
          <div className="meta-row">
            <span className="eyebrow">온보딩 필요</span>
            <span className="muted">프로필 미작성</span>
          </div>
          <div>
            <h2 style={{ marginTop: 0, marginBottom: 8 }}>먼저 기준을 작성해야 합니다</h2>
            <p className="muted" style={{ margin: 0 }}>
              목표 직무와 필수 조건이 비어 있어서 추천 정밀도가 떨어집니다. 온보딩을 완료하면
              이후 평가와 전달 기준에 바로 반영됩니다.
            </p>
          </div>
          <div>
            <Link className="button secondary" href="/onboarding">
              온보딩 작성하기
            </Link>
          </div>
        </div>
      </section>
    );
  }

  return (
    <section className="panel board-card">
      <div className="stack">
        <div className="meta-row">
          <span className="eyebrow">온보딩 완료</span>
          <Link className="button secondary" href="/onboarding">
            수정하기
          </Link>
        </div>
        <div>
          <h2 style={{ marginTop: 0, marginBottom: 8 }}>현재 설정 요약</h2>
          <p className="muted" style={{ margin: 0 }}>
            {summary.role} · {summary.yearsOfExperience}년 경력 · 최소 적합도{" "}
            {summary.minimumFitScore}점
          </p>
        </div>
        <div className="card-grid">
          <article
            style={{
              padding: 18,
              borderRadius: 20,
              border: "1px solid rgba(32, 28, 23, 0.08)",
              background: "rgba(255, 255, 255, 0.58)",
            }}
          >
            <strong>Must-haves</strong>
            <p className="muted" style={{ marginBottom: 0 }}>
              {summary.mustHaves.length > 0 ? summary.mustHaves.join(", ") : "아직 없음"}
            </p>
          </article>
          <article
            style={{
              padding: 18,
              borderRadius: 20,
              border: "1px solid rgba(32, 28, 23, 0.08)",
              background: "rgba(255, 255, 255, 0.58)",
            }}
          >
            <strong>Deal-breakers</strong>
            <p className="muted" style={{ marginBottom: 0 }}>
              {summary.dealBreakers.length > 0 ? summary.dealBreakers.join(", ") : "아직 없음"}
            </p>
          </article>
        </div>
      </div>
    </section>
  );
}
