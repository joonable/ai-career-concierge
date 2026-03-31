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
  preferences?: Preferences;
  guidelines?: Guidelines;
  notification_settings: {
    minimum_fit_score: number;
    delivery_channel?: "slack";
  };
};

export type UserProfileResponse = {
  user_id: string;
  email: string;
  profile_data: ProfileData;
  preferences: Preferences;
  guidelines: Guidelines;
  notification_settings: NotificationSettings;
};

export const EMPTY_PREFERENCES: Preferences = {
  work_modes: [],
  locations: [],
  team_contexts: [],
  skills: {
    preset: [],
    custom: [],
  },
  exclusions: {
    preset: [],
    custom: [],
  },
  comparisons: {},
  note: null,
};

export const EMPTY_PROFILE_DATA: ProfileData = {
  role: "",
  roles: [],
  primary_role: "",
  years_of_experience: 0,
  seniority: "",
  title_keywords: [],
};

export const EMPTY_GUIDELINES: Guidelines = {
  must_haves: [],
  deal_breakers: [],
};

export const EMPTY_USER_PROFILE_RESPONSE: UserProfileResponse = {
  user_id: "",
  email: "",
  profile_data: EMPTY_PROFILE_DATA,
  preferences: EMPTY_PREFERENCES,
  guidelines: EMPTY_GUIDELINES,
  notification_settings: {
    minimum_fit_score: 80,
    delivery_channel: "slack",
  },
};
