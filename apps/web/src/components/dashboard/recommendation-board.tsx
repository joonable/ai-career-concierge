type Recommendation = {
  evaluationId: string;
  status: string;
  fitScore: number | null;
  reasoning: string | null;
  userFeedback: string | null;
  feedbackReason: string | null;
  title: string;
  company: string;
  url: string;
  platform: string;
};

type RecommendationBoardProps = {
  minimumFitScore: number;
  recommendations: Recommendation[];
};

export function RecommendationBoard({
  minimumFitScore,
  recommendations,
}: RecommendationBoardProps) {
  return (
    <section className="board">
      <div className="panel board-card">
        <div className="meta-row">
          <span className="eyebrow">기준 점수</span>
          <span className="score">{minimumFitScore}+</span>
        </div>
        <p className="lead" style={{ marginBottom: 0 }}>
          이 목록은 목업 전용 UI가 아니라 실제 백엔드 대시보드 계약을 그대로 반영합니다.
        </p>
      </div>
      <div className="card-grid">
        {recommendations.length === 0 ? (
          <article className="panel board-card">
            <h2 style={{ marginTop: 0 }}>아직 추천 결과가 없습니다</h2>
            <p className="muted" style={{ marginBottom: 0 }}>
              파이프라인 트리거를 실행해 공고를 수집하고 평가하면 이 보드가 채워집니다.
            </p>
          </article>
        ) : (
          recommendations.map((recommendation) => (
            <article className="panel board-card" key={recommendation.evaluationId}>
              <div className="stack">
                <div className="meta-row">
                  <span className="score">{recommendation.fitScore ?? "대기 중"}</span>
                  <span className="status-pill">{recommendation.status}</span>
                </div>
                <div>
                  <h2 style={{ marginBottom: 8 }}>{recommendation.title}</h2>
                  <p className="muted" style={{ margin: 0 }}>
                    {recommendation.company} · {recommendation.platform}
                  </p>
                </div>
                <p style={{ margin: 0 }}>{recommendation.reasoning ?? "정밀 평가를 기다리는 중입니다."}</p>
                <div className="meta-row">
                  <a className="button secondary" href={recommendation.url} target="_blank">
                    공고 보기
                  </a>
                  {recommendation.userFeedback ? (
                    <span className="muted">
                      피드백: {recommendation.userFeedback}
                      {recommendation.feedbackReason ? ` · ${recommendation.feedbackReason}` : ""}
                    </span>
                  ) : null}
                </div>
              </div>
            </article>
          ))
        )}
      </div>
    </section>
  );
}
