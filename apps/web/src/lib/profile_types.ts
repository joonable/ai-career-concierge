export type ProfileData = {
  role: string;
  roles?: string[];
  primary_role?: string;
  years_of_experience: number;
  seniority?: string;
  title_keywords: string[];
};

export type Guidelines = {
  must_haves: string[];
  deal_breakers: string[];
};

export type PreferenceKeywordBucket = {
  preset: string[];
  custom: string[];
};

export type Preferences = {
  work_modes: string[];
  locations: string[];
  team_contexts: string[];
  skills: PreferenceKeywordBucket;
  exclusions: PreferenceKeywordBucket;
  comparisons: Record<string, number>;
  note: string | null;
};

export type NotificationSettings = {
  minimum_fit_score: number;
  delivery_channel: "slack";
};

export type UserProfilePayload = {
  profile_data: {
    role: string;
    roles?: string[];
    primary_role?: string;
    years_of_experience: number;
    seniority?: string;
    title_keywords?: string[];
  };
  guidelines: Guidelines;
  preferences?: Preferences;
  notification_settings: {
    minimum_fit_score: number;
    delivery_channel?: "slack";
  };
};

export type UserProfileResponse = UserProfilePayload & {
  user_id: string;
  email: string;
  profile_data: ProfileData;
  preferences: Preferences;
  notification_settings: NotificationSettings;
};

export type OnboardingFormState = {
  role: string;
  yearsOfExperience: string;
  mustHaves: string;
  dealBreakers: string;
  minimumFitScore: string;
};

export const EMPTY_ONBOARDING_FORM_STATE: OnboardingFormState = {
  role: "",
  yearsOfExperience: "0",
  mustHaves: "",
  dealBreakers: "",
  minimumFitScore: "80",
};

export function mapProfileToOnboardingFormState(
  profile: UserProfileResponse,
): OnboardingFormState {
  return {
    role: profile.profile_data.role,
    yearsOfExperience: String(profile.profile_data.years_of_experience),
    mustHaves: profile.guidelines.must_haves.join(", "),
    dealBreakers: profile.guidelines.deal_breakers.join(", "),
    minimumFitScore: String(profile.notification_settings.minimum_fit_score),
  };
}

export function mapOnboardingFormStateToProfilePayload(
  state: OnboardingFormState,
): UserProfilePayload {
  return {
    profile_data: {
      role: state.role,
      years_of_experience: Number(state.yearsOfExperience),
    },
    guidelines: {
      must_haves: splitCommaSeparatedValues(state.mustHaves),
      deal_breakers: splitCommaSeparatedValues(state.dealBreakers),
    },
    notification_settings: {
      minimum_fit_score: Number(state.minimumFitScore),
    },
  };
}

function splitCommaSeparatedValues(value: string): string[] {
  return value
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);
}
