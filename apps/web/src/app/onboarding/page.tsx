import { OnboardingForm } from "@/components/profile/onboarding-form";
import { getProfileSnapshot } from "@/lib/api_client_server";
import {
  EMPTY_ONBOARDING_FORM_STATE,
  mapProfileToOnboardingFormState,
} from "@/lib/profile_types";

export default async function OnboardingPage() {
  let initialProfile = EMPTY_ONBOARDING_FORM_STATE;

  try {
    const profile = await getProfileSnapshot();
    initialProfile = mapProfileToOnboardingFormState(profile);
  } catch {
    initialProfile = EMPTY_ONBOARDING_FORM_STATE;
  }

  return (
    <main>
      <div className="shell stack">
        <section className="hero">
          <div className="stack">
            <span className="eyebrow">온보딩</span>
            <h1 className="display">모델이 개입하기 전에 먼저 기준을 조정하세요.</h1>
            <p className="lead">
              목표 직무, 경력 수준, 필수 조건, 비선호 조건, 기본 전달 기준 점수를 설정합니다.
              백엔드는 이를 프로필, 가이드라인, 알림 설정으로 저장해 파이프라인에 사용합니다.
            </p>
          </div>
        </section>
        <OnboardingForm initialProfile={initialProfile} />
      </div>
    </main>
  );
}
