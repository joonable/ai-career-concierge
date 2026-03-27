from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List
from uuid import UUID

from agent.schemas.pipeline_job import PipelineJob
from common.logging import get_logger
from db.enums import LogLevel
from scraper.normalizers.job_normalizer import normalize_scraped_job
from scraper.registry import ScraperRegistry


logger = get_logger(__name__)


@dataclass
class IngestNode:
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
                    normalized_job = normalize_scraped_job(scraped_job)
                    stored_job = self.job_store.upsert_job(normalized_job)
                    current_jobs.append(stored_job)
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
