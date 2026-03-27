export type ProfileData = {
  role: string;
  years_of_experience: number;
  title_keywords: string[];
};

export type Guidelines = {
  must_haves: string[];
  deal_breakers: string[];
};

export type NotificationSettings = {
  minimum_fit_score: number;
  delivery_channel: string | null;
};

export type UserProfilePayload = {
  profile_data: ProfileData;
  guidelines: Guidelines;
  notification_settings: NotificationSettings;
};

export type UserProfileResponse = UserProfilePayload & {
  user_id: string;
  email: string;
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
