from __future__ import annotations

from api.dependencies.auth import UserIdentity
from api.schemas.users import DashboardRecommendation, DashboardResponse


class DashboardService:
    def __init__(
        self,
        user_store,
        evaluation_store,
    ):
        self.user_store = user_store
        self.evaluation_store = evaluation_store

    def get_dashboard(self, identity: UserIdentity) -> DashboardResponse:
        user = self.user_store.upsert_from_identity(identity)
        rows = self.evaluation_store.list_dashboard_rows(user.user_id)

        recommendations = [
            DashboardRecommendation(
                evaluation_id=row.evaluation_id,
                status=row.status,
                fit_score=row.fit_score,
                reasoning=row.reasoning,
                rule_rejection_reason=row.rule_rejection_reason,
                user_feedback=row.user_feedback,
                feedback_reason=row.feedback_reason,
                created_at=row.created_at,
                updated_at=row.updated_at,
                job_id=row.job_id,
                title=row.title,
                company=row.company,
                url=row.url,
                platform=row.platform,
                jd_raw_text=row.jd_raw_text,
                min_years_experience=row.min_years_experience,
                max_years_experience=row.max_years_experience,
                source_metadata=row.source_metadata,
            )
            for row in rows
        ]
        return DashboardResponse(
            user_id=user.user_id,
            minimum_fit_score=user.notification_settings.minimum_fit_score,
            recommendations=recommendations,
        )
