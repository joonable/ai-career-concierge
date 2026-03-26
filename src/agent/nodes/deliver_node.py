from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Protocol


class SlackNotifier(Protocol):
    async def send_recommendation(self, *, user_context: Dict[str, Any], evaluation_result) -> None:
        ...


@dataclass
class DeliverNode:
    slack_notifier: SlackNotifier

    async def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        notification_settings = state["user_context"].get("notification_settings", {})
        threshold = int(notification_settings.get("minimum_fit_score", 80))

        for evaluation_result in state.get("evaluation_results", []):
            if evaluation_result.fit_score < threshold:
                continue

            await self.slack_notifier.send_recommendation(
                user_context=state["user_context"],
                evaluation_result=evaluation_result,
            )

        return {}
