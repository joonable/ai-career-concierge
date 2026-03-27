import type { UserProfileResponse } from "@/lib/profile_types";

type DashboardOnboardingSource = Pick<
  UserProfileResponse,
  "profile_data" | "guidelines" | "notification_settings"
>;

export type DashboardOnboardingFieldKey = "role" | "must_haves" | "deal_breakers";

export type DashboardOnboardingField = {
  key: DashboardOnboardingFieldKey;
  label: string;
  detail: string;
  isComplete: boolean;
  statusLabel: "입력됨" | "미입력";
};

export type DashboardOnboardingState = {
  isComplete: boolean;
  completionLabel: string;
  completedCount: number;
  requiredCount: number;
  missingFields: DashboardOnboardingFieldKey[];
  fields: DashboardOnboardingField[];
  role: string;
  yearsOfExperience: number;
  mustHaves: string[];
  dealBreakers: string[];
  minimumFitScore: number;
};

export function deriveDashboardOnboardingState(
  profile: DashboardOnboardingSource,
): DashboardOnboardingState {
  const role = profile.profile_data.role.trim();
  const mustHaves = normalizeList(profile.guidelines.must_haves);
  const dealBreakers = normalizeList(profile.guidelines.deal_breakers);

  const fields: DashboardOnboardingField[] = [
    {
      key: "role",
      label: "목표 직무",
      detail: role || "아직 입력되지 않음",
      isComplete: role.length > 0,
      statusLabel: role.length > 0 ? "입력됨" : "미입력",
    },
    {
      key: "must_haves",
      label: "필수 조건",
      detail: mustHaves.length > 0 ? `${mustHaves.length}개 입력됨` : "아직 입력되지 않음",
      isComplete: mustHaves.length > 0,
      statusLabel: mustHaves.length > 0 ? "입력됨" : "미입력",
    },
    {
      key: "deal_breakers",
      label: "비선호 조건",
      detail:
        dealBreakers.length > 0 ? `${dealBreakers.length}개 입력됨` : "아직 입력되지 않음",
      isComplete: dealBreakers.length > 0,
      statusLabel: dealBreakers.length > 0 ? "입력됨" : "미입력",
    },
  ];

  const completedCount = fields.filter((field) => field.isComplete).length;
  const requiredCount = fields.length;
  const isComplete = completedCount === requiredCount;

  return {
    isComplete,
    completionLabel: `${completedCount}/${requiredCount} 입력`,
    completedCount,
    requiredCount,
    missingFields: fields.filter((field) => !field.isComplete).map((field) => field.key),
    fields,
    role,
    yearsOfExperience: profile.profile_data.years_of_experience,
    mustHaves,
    dealBreakers,
    minimumFitScore: profile.notification_settings.minimum_fit_score,
  };
}

function normalizeList(values: string[]) {
  return values.map((value) => value.trim()).filter(Boolean);
}
