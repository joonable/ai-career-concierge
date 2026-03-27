import { OnboardingStatusCard } from "@/components/dashboard/onboarding-status-card";
import { RecommendationBoard } from "@/components/dashboard/recommendation-board";
import { getDashboardSnapshot, getProfileSnapshot } from "@/lib/api_client_server";
import { mapDashboardRecommendations } from "@/lib/dashboard_mapper";

export default async function DashboardPage() {
  const [dashboard, profile] = await Promise.all([getDashboardSnapshot(), getProfileSnapshot()]);
  const recommendations = mapDashboardRecommendations(dashboard);
  const isOnboardingComplete = profile.profile_data.role.trim().length > 0;

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
        <OnboardingStatusCard
          summary={{
            isComplete: isOnboardingComplete,
            role: profile.profile_data.role,
            yearsOfExperience: profile.profile_data.years_of_experience,
            mustHaves: profile.guidelines.must_haves,
            dealBreakers: profile.guidelines.deal_breakers,
            minimumFitScore: profile.notification_settings.minimum_fit_score,
          }}
        />
        <RecommendationBoard
          minimumFitScore={dashboard.minimum_fit_score}
          recommendations={recommendations}
        />
      </div>
    </main>
  );
}
