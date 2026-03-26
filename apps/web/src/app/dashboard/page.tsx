import { RecommendationBoard } from "@/components/dashboard/recommendation-board";
import { getDashboardSnapshot } from "@/lib/api_client";
import { mapDashboardRecommendations } from "@/lib/dashboard_mapper";

export default async function DashboardPage() {
  const dashboard = await getDashboardSnapshot();
  const recommendations = mapDashboardRecommendations(dashboard);

  return (
    <main>
      <div className="shell stack">
        <section className="hero">
          <div className="stack">
            <span className="eyebrow">Daily shortlist</span>
            <h1 className="display">Only the roles that survived the full pipeline.</h1>
            <p className="lead">
              This board is intentionally narrow. It mirrors the backend contract for
              recommendation review and feedback, without expanding into broader dashboard
              complexity before the PoC loop works.
            </p>
          </div>
        </section>
        <RecommendationBoard
          minimumFitScore={dashboard.minimum_fit_score}
          recommendations={recommendations}
        />
      </div>
    </main>
  );
}
