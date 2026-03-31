export type PromptOpsBacklogItem = {
  title: string;
  url: string;
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
