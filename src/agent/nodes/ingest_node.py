from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List
from uuid import UUID

from agent.schemas.pipeline_job import PipelineJob
from common.logging import get_logger
from db.enums import LogLevel
from scraper.normalizers.job_normalizer import InvalidScrapedJobError
from scraper.normalizers.job_normalizer import normalize_scraped_job
from scraper.registry import ScraperRegistry


logger = get_logger(__name__)


@dataclass
class IngestNode:
    """
    LangGraph 파이프라인의 첫 번째 단계(노드)입니다.
    등록된 스크래퍼(ScraperRegistry) 모델들을 사용하여 대상 채용 플랫폼에서 비동기적으로 새로운 채용 공고를 수집하고,
    동일한 형식으로 정규화(Normalization)하여 중복을 거르고 데이터베이스에 저장(upsert)합니다.
    스크래퍼에서 장애가 발생해도 파이프라인을 멈추지 않고(Graceful Degradation) System_Log에 에러를 기록한 후 건너뜁니다.
    """
    scraper_registry: ScraperRegistry
    job_store: object
    system_log_store: object

    async def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        user_id = UUID(str(state["user_context"]["user_id"]))
        current_jobs: List[PipelineJob] = []
        source_errors = list(state.get("source_errors", []))

        for source in self.scraper_registry.sources:
            try:
                scraped_jobs = await source.fetch_jobs(state["user_context"])
                for scraped_job in scraped_jobs:
                    try:
                        normalized_job = normalize_scraped_job(scraped_job)
                        stored_job = self.job_store.upsert_job(normalized_job)
                        current_jobs.append(stored_job)
                    except InvalidScrapedJobError as exc:
                        logger.warning(
                            "Discarded invalid scraped job before storage.",
                            extra={
                                "source": source.source_name,
                                "external_job_id": getattr(scraped_job, "external_job_id", ""),
                                "discard_reason": str(exc),
                            },
                        )
            except Exception as exc:  # pragma: no cover - exercised by resilience tests
                logger.exception("Scraper source failed.", extra={"source": source.source_name})
                source_errors.append(source.source_name)
                self.system_log_store.create(
                    run_id=state["run_id"],
                    event_type="scraper_failure",
                    level=LogLevel.ERROR,
                    message=f"{source.source_name} failed: {exc}",
                    user_id=user_id,
                    platform=source.source_name,
                    metadata={"error_type": exc.__class__.__name__},
                )

        return {
            "current_jobs": current_jobs,
            "source_errors": source_errors,
        }
