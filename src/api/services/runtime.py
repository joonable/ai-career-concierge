from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from api.services.gemini_evaluator import GeminiEvaluator
from api.services.mock_llm_evaluator import MockGeminiEvaluator
from api.services.slack_notifier import LoggingSlackNotifier
from api.services.slack_signature_service import SlackSignatureService
from common.config import Settings
from scraper.registry import ScraperRegistry
from scraper.sources.incruit import IncruitScraper
from scraper.sources.mock_platform import MockPlatformScraper


@dataclass(frozen=True)
class RuntimeServices:
    scraper_registry: ScraperRegistry
    llm_evaluator: Any
    slack_notifier: LoggingSlackNotifier
    slack_signature_service: SlackSignatureService


def build_default_runtime(settings: Settings) -> RuntimeServices:
    signing_secret = settings.slack_signing_secret or "dev-slack-secret"
    if not settings.gemini_api_key:
        raise ValueError("GEMINI_API_KEY is required for the default runtime evaluator.")
    return RuntimeServices(
        scraper_registry=ScraperRegistry(
            [
                IncruitScraper(
                    headless=settings.scraper_headless,
                    timeout_ms=settings.scraper_timeout_ms,
                    max_pages=settings.scraper_max_pages,
                    base_url=settings.scraper_incruit_base_url,
                )
            ]
        ),
        llm_evaluator=GeminiEvaluator(
            api_key=settings.gemini_api_key,
            model=settings.gemini_model,
        ),
        slack_notifier=LoggingSlackNotifier(),
        slack_signature_service=SlackSignatureService(signing_secret),
    )
