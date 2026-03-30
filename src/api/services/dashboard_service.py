from __future__ import annotations

from api.dependencies.auth import UserIdentity
from api.schemas.users import DashboardRecommendation, DashboardResponse
from api.services.dashboard_detail_builder import build_dashboard_detail_fields


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

        recommendations = []
        for row in rows:
            detail_fields = build_dashboard_detail_fields(
                row=row,
                user=user,
                minimum_fit_score=user.notification_settings.minimum_fit_score,
            )
            recommendations.append(
                DashboardRecommendation(
                    evaluation_id=row.evaluation_id,
                    status=row.status,
                    fit_score=row.fit_score,
                    reasoning=row.reasoning,
                    decision_summary=detail_fields["decision_summary"],
                    match_highlights=detail_fields["match_highlights"],
                    risk_highlights=detail_fields["risk_highlights"],
                    confidence_level=detail_fields["confidence_level"],
                    rule_rejection_reason=row.rule_rejection_reason,
                    rule_match_reasons=detail_fields["rule_match_reasons"],
                    rule_rejection_details=detail_fields["rule_rejection_details"],
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
                    responsibilities=detail_fields["responsibilities"],
                    requirements=detail_fields["requirements"],
                    preferred_requirements=detail_fields["preferred_requirements"],
                    location=detail_fields["location"],
                    employment_type=detail_fields["employment_type"],
                )
            )
        return DashboardResponse(
            user_id=user.user_id,
            minimum_fit_score=user.notification_settings.minimum_fit_score,
            recommendations=recommendations,
        )
