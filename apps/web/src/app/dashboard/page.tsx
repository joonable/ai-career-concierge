import { RecommendationBoard } from "@/components/dashboard/recommendation-board";
import { getDashboardSnapshot } from "@/lib/api_client_server";
import { mapDashboardRecommendations } from "@/lib/dashboard_mapper";

export default async function DashboardPage() {
  const dashboard = await getDashboardSnapshot();
  const recommendations = mapDashboardRecommendations(dashboard);

  return (
    <main>
      <div className="shell stack">
        <section className="hero">
          <div className="stack">
            <span className="eyebrow">오늘의 추천 목록</span>
            <h1 className="display">전체 파이프라인을 통과한 공고만 남깁니다.</h1>
            <p className="lead">
              이 보드는 의도적으로 좁게 설계했습니다. PoC 루프가 먼저 안정적으로 동작하도록,
              추천 검토와 피드백에 필요한 백엔드 계약만 그대로 반영합니다.
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
