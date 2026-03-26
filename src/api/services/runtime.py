from __future__ import annotations

from dataclasses import dataclass

from api.services.mock_llm_evaluator import MockGeminiEvaluator
from api.services.slack_notifier import LoggingSlackNotifier
from api.services.slack_signature_service import SlackSignatureService
from common.config import Settings
from scraper.registry import ScraperRegistry
from scraper.sources.mock_platform import MockPlatformScraper


@dataclass(frozen=True)
class RuntimeServices:
    scraper_registry: ScraperRegistry
    llm_evaluator: MockGeminiEvaluator
    slack_notifier: LoggingSlackNotifier
    slack_signature_service: SlackSignatureService


def build_default_runtime(settings: Settings) -> RuntimeServices:
    signing_secret = settings.slack_signing_secret or "dev-slack-secret"
    return RuntimeServices(
        scraper_registry=ScraperRegistry([MockPlatformScraper()]),
        llm_evaluator=MockGeminiEvaluator(),
        slack_notifier=LoggingSlackNotifier(),
        slack_signature_service=SlackSignatureService(signing_secret),
    )
