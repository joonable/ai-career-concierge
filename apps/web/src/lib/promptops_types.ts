export type PromptOpsBacklogItem = {
  title: string;
  url: string;
};

export type PromptOpsDatasetItem = {
  id: string;
  scenario_type: string;
  scenario_family: string;
  difficulty: string;
  should_pass: boolean;
  fit_score_min: number;
  fit_score_max: number;
  scoring_note: string;
  job_title: string;
};

export type PromptOpsDatasetResponse = {
  total: number;
  items: PromptOpsDatasetItem[];
};

export type PromptOpsStatusResponse = {
  prompt_family: string;
  production_identifier: string;
  staging_identifier: string;
  candidate_identifier: string;
  latest_decision: string;
  compare_url: string;
  review_queue_name: string;
  review_queue_url: string;
  notion_backlog_url: string;
  latest_iteration_title: string;
  latest_iteration_url: string;
  latest_summary: string[];
  next_backlog_items: PromptOpsBacklogItem[];
};
