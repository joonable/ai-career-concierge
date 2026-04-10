from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from agent.prompts import PromptManager
from api.services.gemini_evaluator import GeminiEvaluator
from api.services.slack_notifier import LoggingSlackNotifier
from api.services.slack_signature_service import SlackSignatureService
from common.config import Settings
from common.telemetry import LangSmithTracer
from scraper.registry import ScraperRegistry
from scraper.sources.incruit import IncruitScraper


@dataclass(frozen=True)
class RuntimeServices:
    scraper_registry: ScraperRegistry
    llm_evaluator: Any
    prompt_manager: PromptManager
    slack_notifier: LoggingSlackNotifier
    slack_signature_service: SlackSignatureService
    langsmith_tracer: LangSmithTracer
    pipeline_version: str


def build_default_runtime(settings: Settings) -> RuntimeServices:
    signing_secret = settings.slack_signing_secret or "dev-slack-secret"
    if not settings.gemini_api_key:
        raise ValueError("GEMINI_API_KEY is required for the default runtime evaluator.")
    langsmith_tracer = LangSmithTracer.from_settings(settings)
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
        prompt_manager=PromptManager.from_settings(settings, client=langsmith_tracer.client),
        slack_notifier=LoggingSlackNotifier(),
        slack_signature_service=SlackSignatureService(signing_secret),
        langsmith_tracer=langsmith_tracer,
        pipeline_version=settings.pipeline_version,
    )
