from __future__ import annotations

from fastapi import HTTPException, status

from api.dependencies.auth import UserIdentity
from api.schemas.users import (
    PromptOpsBacklogItem,
    PromptOpsStatusResponse,
)
from common.config import Settings, get_settings
from promptops.core.registry import get_prompt_family


LANGSMITH_WORKSPACE_ID = "a5f5f699-f384-58ec-9be0-2a39bb96969e"
LANGSMITH_BASE_URL = "https://smith.langchain.com"
PROMPTOPS_REVIEW_QUEUE_ID = "a1438ae9-2449-4798-94f1-0243ab9b1e18"
PROMPTOPS_REVIEW_QUEUE_NAME = "job-evaluation-review"
PROMPTOPS_NOTION_BACKLOG_URL = "https://www.notion.so/c5fb7393ece54107b445e90bdabab642"
PROMPTOPS_COMPARE_URL = (
    "https://smith.langchain.com/o/a5f5f699-f384-58ec-9be0-2a39bb96969e/"
    "datasets/277c4ae5-c460-4be4-8895-732911768cd7/compare"
    "?selectedSessions=4906f684-12db-4c1a-88d0-782d25f5bbda"
    "&selectedSessions=91e3e1bf-e2a1-426c-a155-ce616568eabd"
)
PROMPTOPS_LATEST_ITERATION_TITLE = "Job Evaluation 반복 개선 기록 001"
PROMPTOPS_LATEST_ITERATION_URL = "/internal/prompts/iterations/job-evaluation-001"

PROMPTOPS_LATEST_SUMMARY = [
    "최신 `job-evaluation:staging` 프롬프트 1회 검증에서 fit_score_band는 0.9333, classification_match는 1.0을 기록했습니다.",
    "deal_breaker_severity_match, hard_reject_penalty, summary_concise도 모두 1.0으로 유지됐습니다.",
    "반면 concern_keywords_match 0.2667, confidence_alignment 0.4, strength_keywords_match 0.2로 설명 품질 축은 여전히 보강이 필요합니다.",
]

PROMPTOPS_BACKLOG_ITEMS = [
    PromptOpsBacklogItem(
        title="인접 infra 역할의 role alignment 문구 다듬기",
        url="https://www.notion.so/3347099bf2cc81debc98c6eb6d1f925d",
    ),
    PromptOpsBacklogItem(
        title="borderline 역할의 must-have coverage 처리 보강",
        url="https://www.notion.so/3347099bf2cc81ddbd70d5e97b4e10e0",
    ),
    PromptOpsBacklogItem(
        title="인접 역할의 transferable skill credit 명확화",
        url="https://www.notion.so/3347099bf2cc8102b0efeae13925b3ff",
    ),
]


class PromptOpsStatusService:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    def get_status(self, identity: UserIdentity) -> PromptOpsStatusResponse:
        self.ensure_access(identity)
        family = get_prompt_family("job-evaluation")

        return PromptOpsStatusResponse(
            prompt_family=family.key,
            production_identifier=family.metadata.tags["production"],
            staging_identifier=family.metadata.tags["staging"],
            candidate_identifier=f"{family.metadata.tags['candidate']} · local-v4 (직전 후보안)",
            latest_decision="최신 staging 프롬프트 1회 검증 완료, 승격 보류",
            compare_url=PROMPTOPS_COMPARE_URL,
            review_queue_name=PROMPTOPS_REVIEW_QUEUE_NAME,
            review_queue_url=self._build_review_queue_url(),
            notion_backlog_url=PROMPTOPS_NOTION_BACKLOG_URL,
            latest_iteration_title=PROMPTOPS_LATEST_ITERATION_TITLE,
            latest_iteration_url=PROMPTOPS_LATEST_ITERATION_URL,
            latest_summary=PROMPTOPS_LATEST_SUMMARY,
            next_backlog_items=PROMPTOPS_BACKLOG_ITEMS,
        )

    def ensure_access(self, identity: UserIdentity) -> None:
        allowed_emails = {email.lower() for email in self.settings.promptops_admin_emails}
        email = identity.email.strip().lower()
        if not allowed_emails or email not in allowed_emails:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found.")

    def _build_review_queue_url(self) -> str:
        return (
            f"{LANGSMITH_BASE_URL}/o/{LANGSMITH_WORKSPACE_ID}/annotation-queues/"
            f"{PROMPTOPS_REVIEW_QUEUE_ID}"
        )
