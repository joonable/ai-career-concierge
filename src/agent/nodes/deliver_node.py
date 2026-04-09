from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Protocol


class SlackNotifier(Protocol):
    async def send_recommendation(self, *, user_context: Dict[str, Any], evaluation_result) -> None: ...


@dataclass
class DeliverNode:
    """
    LangGraph 파이프라인의 마지막(네 번째) 단계입니다.
    LLMEvalNode에서 완료된 평가 결과들 중, 사용자가 설정한 알림 조건 기준 점수(minimum_fit_score, 기본값 80점) 이상을 획득한
    핵심 추천 공고들만 추려내어 Slack Webhook 등을 통해 사용자에게 최종 알림을 전송(deliver)합니다.
    """

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
