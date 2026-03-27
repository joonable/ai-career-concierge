from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List
from uuid import UUID

from agent.schemas.pipeline_job import PipelineJob
from db.enums import EvaluationStatus


def _title_matches(job: PipelineJob, user_context: Dict[str, Any]) -> bool:
    profile_data = user_context.get("profile_data", {})
    role = str(profile_data.get("role", "")).lower().strip()
    keywords = [keyword.lower() for keyword in profile_data.get("title_keywords", [])]

    if role and role in job.title.lower():
        return True

    return any(keyword in job.title.lower() for keyword in keywords)


def _experience_matches(job: PipelineJob, user_context: Dict[str, Any]) -> bool:
    years = user_context.get("profile_data", {}).get("years_of_experience")
    if years is None:
        return True

    if job.min_years_experience is not None and years < job.min_years_experience:
        return False

    if job.max_years_experience is not None and years > job.max_years_experience:
        return False

    return True


@dataclass
class RuleFilterNode:
    evaluation_store: object

    async def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        user_id = UUID(str(state["user_context"]["user_id"]))
        filtered_jobs: List[PipelineJob] = []

        for job in state.get("current_jobs", []):
            existing_evaluation = self.evaluation_store.get_by_user_and_job(user_id, job.job_id)
            if existing_evaluation is not None and existing_evaluation.status != EvaluationStatus.PENDING:
                continue

            if not _title_matches(job, state["user_context"]):
                self.evaluation_store.mark_rule_rejected(
                    user_id=user_id,
                    job_id=job.job_id,
                    reason="TITLE_MISMATCH",
                )
                continue

            if not _experience_matches(job, state["user_context"]):
                self.evaluation_store.mark_rule_rejected(
                    user_id=user_id,
                    job_id=job.job_id,
                    reason="EXPERIENCE_MISMATCH",
                )
                continue

            self.evaluation_store.ensure_pending(user_id=user_id, job_id=job.job_id)
            filtered_jobs.append(job)

        return {"current_jobs": filtered_jobs}
