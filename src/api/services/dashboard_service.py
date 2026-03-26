from __future__ import annotations

from api.dependencies.auth import UserIdentity
from api.schemas.users import DashboardRecommendation, DashboardResponse
from db.repositories import EvaluationRepository, UserRepository


class DashboardService:
    def __init__(
        self,
        user_repository: UserRepository,
        evaluation_repository: EvaluationRepository,
    ):
        self.user_repository = user_repository
        self.evaluation_repository = evaluation_repository

    def get_dashboard(self, identity: UserIdentity) -> DashboardResponse:
        user = self.user_repository.upsert_from_identity(
            email=identity.email,
            oauth_id=identity.oauth_id,
            preferred_user_id=identity.user_id,
        )
        notification_settings = user.notification_settings or {"minimum_fit_score": 80}
        rows = self.evaluation_repository.list_dashboard_rows(user.id)

        recommendations = [
            DashboardRecommendation(
                evaluation_id=evaluation.id,
                status=evaluation.status,
                fit_score=evaluation.fit_score,
                reasoning=evaluation.reasoning,
                user_feedback=evaluation.user_feedback,
                feedback_reason=evaluation.feedback_reason,
                job_id=job.id,
                title=job.title,
                company=job.company,
                url=job.url,
                platform=job.platform,
            )
            for evaluation, job in rows
        ]
        return DashboardResponse(
            user_id=user.id,
            minimum_fit_score=int(notification_settings.get("minimum_fit_score", 80)),
            recommendations=recommendations,
        )
