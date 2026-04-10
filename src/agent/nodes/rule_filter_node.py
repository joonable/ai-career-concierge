from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List
from uuid import UUID

from agent.schemas.pipeline_job import PipelineJob
from common.user_preferences import build_normalized_stored_preferences
from db.enums import EvaluationStatus


def _title_matches(job: PipelineJob, user_context: Dict[str, Any]) -> bool:
    preferences = build_normalized_stored_preferences(user_context)
    role = preferences.target_role.lower().strip()
    keywords = [keyword.lower() for keyword in preferences.title_keywords]

    if role and role in job.title.lower():
        return True

    return any(keyword in job.title.lower() for keyword in keywords)


def _experience_matches(job: PipelineJob, user_context: Dict[str, Any]) -> bool:
    years = build_normalized_stored_preferences(user_context).years_of_experience
    if years is None:
        return True

    if job.min_years_experience is not None and years < job.min_years_experience:
        return False

    return not (job.max_years_experience is not None and years > job.max_years_experience)


def _location_matches(job: PipelineJob, user_context: Dict[str, Any]) -> bool:
    preferences = build_normalized_stored_preferences(user_context)
    if not preferences.locations:
        return True

    source_metadata = job.source_metadata if isinstance(job.source_metadata, dict) else {}
    location_text = " ".join(
        [
            str(source_metadata.get("location", "") or ""),
            str(source_metadata.get("region", "") or ""),
            str(source_metadata.get("workplace", "") or ""),
            job.jd_raw_text,
        ]
    ).lower()
    if not location_text.strip():
        return True

    aliases = {
        "서울": ["seoul", "서울"],
        "판교": ["pangyo", "판교"],
        "분당": ["bundang", "분당"],
        "경기권": ["gyeonggi", "경기", "수원", "성남"],
        "대전": ["daejeon", "대전"],
        "부산": ["busan", "부산"],
        "전국 어디든": [],
        "해외 포함": ["global", "overseas", "remote worldwide", "international", "해외"],
    }
    if "전국 어디든" in preferences.locations:
        return True

    return any(
        any(alias in location_text for alias in aliases.get(location, [location.lower()]))
        for location in preferences.locations
    )


def _work_mode_matches(job: PipelineJob, user_context: Dict[str, Any]) -> bool:
    preferences = build_normalized_stored_preferences(user_context)
    if not preferences.work_modes:
        return True

    source_metadata = job.source_metadata if isinstance(job.source_metadata, dict) else {}
    work_mode_text = " ".join(
        [
            str(source_metadata.get("employment_type", "") or ""),
            str(source_metadata.get("employmentType", "") or ""),
            str(source_metadata.get("workplace", "") or ""),
            job.jd_raw_text,
        ]
    ).lower()
    if not work_mode_text.strip():
        return True

    aliases = {
        "원격": ["remote", "원격", "재택"],
        "하이브리드": ["hybrid", "하이브리드"],
        "상주 출근": ["onsite", "on-site", "office", "출근", "상주"],
    }
    return any(
        any(alias in work_mode_text for alias in aliases.get(mode, [mode.lower()])) for mode in preferences.work_modes
    )


@dataclass
class RuleFilterNode:
    """
    LangGraph 파이프라인의 두 번째 단계입니다.
    LLM API 호출 비용을 획기적으로 낮추기 위해, 수집된 공고들을 대상으로 규칙 기반(Rule-based)의 1차 필터링을 수행합니다.

    주요 역할:
    - 이미 평가된 이력이 있는 공고 제외
    - 사용자의 선호 조건과 직무명(title), 연차(experience), 최소/최대 근무지(location), 근무 형태(work_mode) 비교
    - 탈락한 공고는 DB에 'RULE_REJECTED' 상태 및 거절 사유와 함께 기록
    """

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

            if not _location_matches(job, state["user_context"]):
                self.evaluation_store.mark_rule_rejected(
                    user_id=user_id,
                    job_id=job.job_id,
                    reason="LOCATION_MISMATCH",
                )
                continue

            if not _work_mode_matches(job, state["user_context"]):
                self.evaluation_store.mark_rule_rejected(
                    user_id=user_id,
                    job_id=job.job_id,
                    reason="WORK_MODE_MISMATCH",
                )
                continue

            self.evaluation_store.ensure_pending(user_id=user_id, job_id=job.job_id)
            filtered_jobs.append(job)

        return {"current_jobs": filtered_jobs}
