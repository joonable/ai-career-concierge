import { deriveDashboardProfileSummary } from "@/lib/dashboard_profile";
import type { UserProfileResponse } from "@/lib/profile_types";

type DashboardOnboardingSource = Pick<
  UserProfileResponse,
  "profile_data" | "guidelines" | "preferences" | "notification_settings"
>;

export type DashboardOnboardingFieldKey = "role" | "skills" | "exclusions";

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
  preferredSkills: string[];
  exclusions: string[];
  workModes: string[];
  locations: string[];
  teamContexts: string[];
  minimumFitScore: number;
};

export function deriveDashboardOnboardingState(
  profile: DashboardOnboardingSource,
): DashboardOnboardingState {
  const summary = deriveDashboardProfileSummary(profile);
  const role = summary.role;

  const fields: DashboardOnboardingField[] = [
    {
      key: "role",
      label: "목표 직무",
      detail: role || "아직 입력되지 않음",
      isComplete: role.length > 0,
      statusLabel: role.length > 0 ? "입력됨" : "미입력",
    },
    {
      key: "skills",
      label: "중요 스킬",
      detail:
        summary.preferredSkills.length > 0
          ? `${summary.preferredSkills.length}개 입력됨`
          : "아직 입력되지 않음",
      isComplete: summary.preferredSkills.length > 0,
      statusLabel: summary.preferredSkills.length > 0 ? "입력됨" : "미입력",
    },
    {
      key: "exclusions",
      label: "제외 조건",
      detail:
        summary.exclusions.length > 0 ? `${summary.exclusions.length}개 입력됨` : "아직 입력되지 않음",
      isComplete: summary.exclusions.length > 0,
      statusLabel: summary.exclusions.length > 0 ? "입력됨" : "미입력",
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
    yearsOfExperience: summary.yearsOfExperience,
    preferredSkills: summary.preferredSkills,
    exclusions: summary.exclusions,
    workModes: summary.workModes,
    locations: summary.locations,
    teamContexts: summary.teamContexts,
    minimumFitScore: summary.minimumFitScore,
  };
}
