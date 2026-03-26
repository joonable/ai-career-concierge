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
          <span className="eyebrow">Threshold</span>
          <span className="score">{minimumFitScore}+</span>
        </div>
        <p className="lead" style={{ marginBottom: 0 }}>
          Recommendations here reflect the backend dashboard contract, not a mock-only UI state.
        </p>
      </div>
      <div className="card-grid">
        {recommendations.length === 0 ? (
          <article className="panel board-card">
            <h2 style={{ marginTop: 0 }}>No recommendations yet</h2>
            <p className="muted" style={{ marginBottom: 0 }}>
              Run the pipeline trigger to ingest jobs, evaluate them, and populate this board.
            </p>
          </article>
        ) : (
          recommendations.map((recommendation) => (
            <article className="panel board-card" key={recommendation.evaluationId}>
              <div className="stack">
                <div className="meta-row">
                  <span className="score">{recommendation.fitScore ?? "Pending"}</span>
                  <span className="status-pill">{recommendation.status}</span>
                </div>
                <div>
                  <h2 style={{ marginBottom: 8 }}>{recommendation.title}</h2>
                  <p className="muted" style={{ margin: 0 }}>
                    {recommendation.company} · {recommendation.platform}
                  </p>
                </div>
                <p style={{ margin: 0 }}>{recommendation.reasoning ?? "Awaiting deep evaluation."}</p>
                <div className="meta-row">
                  <a className="button secondary" href={recommendation.url} target="_blank">
                    View job
                  </a>
                  {recommendation.userFeedback ? (
                    <span className="muted">
                      Feedback: {recommendation.userFeedback}
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
