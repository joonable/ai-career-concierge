export type DashboardApiRecommendation = {
  evaluation_id: string;
  status: string;
  fit_score: number | null;
  reasoning: string | null;
  decision_summary: string | null;
  match_highlights: string[];
  risk_highlights: string[];
  confidence_level: string;
  rule_rejection_reason: string | null;
  rule_match_reasons: string[];
  rule_rejection_details: string[];
  user_feedback: string | null;
  feedback_reason: string | null;
  created_at: string;
  updated_at: string;
  job_id: string;
  title: string;
  company: string;
  url: string;
  platform: string;
  jd_raw_text: string;
  min_years_experience: number | null;
  max_years_experience: number | null;
  source_metadata: Record<string, unknown>;
  responsibilities: string[];
  requirements: string[];
  preferred_requirements: string[];
  location: string | null;
  employment_type: string | null;
};

export type DashboardResponse = {
  user_id: string;
  minimum_fit_score: number;
  recommendations: DashboardApiRecommendation[];
};
