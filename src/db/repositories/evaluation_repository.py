from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
from uuid import UUID

from sqlmodel import Session, select

from db.enums import EvaluationStatus, FeedbackState
from db.models import Evaluation, Job


class EvaluationRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_user_and_job(self, user_id: UUID, job_id: UUID) -> Optional[Evaluation]:
        statement = select(Evaluation).where(
            Evaluation.user_id == user_id,
            Evaluation.job_id == job_id,
        )
        return self.session.exec(statement).first()

    def ensure_pending(self, user_id: UUID, job_id: UUID) -> Evaluation:
        evaluation = self.get_by_user_and_job(user_id, job_id)
        if evaluation is None:
            evaluation = Evaluation(user_id=user_id, job_id=job_id, status=EvaluationStatus.PENDING)
        else:
            evaluation.status = EvaluationStatus.PENDING
            evaluation.rule_rejection_reason = None

        evaluation.updated_at = datetime.now(timezone.utc)
        self.session.add(evaluation)
        self.session.commit()
        self.session.refresh(evaluation)
        return evaluation

    def mark_rule_rejected(self, user_id: UUID, job_id: UUID, reason: str) -> Evaluation:
        evaluation = self.get_by_user_and_job(user_id, job_id)
        if evaluation is None:
            evaluation = Evaluation(user_id=user_id, job_id=job_id)

        evaluation.status = EvaluationStatus.RULE_REJECTED
        evaluation.rule_rejection_reason = reason
        evaluation.fit_score = None
        evaluation.reasoning = None
        evaluation.updated_at = datetime.now(timezone.utc)

        self.session.add(evaluation)
        self.session.commit()
        self.session.refresh(evaluation)
        return evaluation

    def mark_llm_evaluated(
        self,
        user_id: UUID,
        job_id: UUID,
        fit_score: int,
        reasoning: str,
    ) -> Evaluation:
        evaluation = self.get_by_user_and_job(user_id, job_id)
        if evaluation is None:
            evaluation = Evaluation(user_id=user_id, job_id=job_id)

        evaluation.status = EvaluationStatus.LLM_EVALUATED
        evaluation.fit_score = fit_score
        evaluation.reasoning = reasoning
        evaluation.rule_rejection_reason = None
        evaluation.updated_at = datetime.now(timezone.utc)

        self.session.add(evaluation)
        self.session.commit()
        self.session.refresh(evaluation)
        return evaluation

    def update_feedback(
        self,
        evaluation_id: UUID,
        feedback: FeedbackState,
        feedback_reason: Optional[str] = None,
    ) -> Evaluation:
        evaluation = self.session.get(Evaluation, evaluation_id)
        if evaluation is None:
            raise ValueError("Evaluation not found.")

        evaluation.user_feedback = feedback
        evaluation.feedback_reason = feedback_reason
        evaluation.updated_at = datetime.now(timezone.utc)

        self.session.add(evaluation)
        self.session.commit()
        self.session.refresh(evaluation)
        return evaluation

    def list_recent_dislikes(self, user_id: UUID, limit: int = 10) -> List[str]:
        statement = (
            select(Evaluation.feedback_reason)
            .where(
                Evaluation.user_id == user_id,
                Evaluation.user_feedback == FeedbackState.DISLIKE,
                Evaluation.feedback_reason.is_not(None),
            )
            .order_by(Evaluation.updated_at.desc())
            .limit(limit)
        )
        return [reason for reason in self.session.exec(statement).all() if reason]

    def list_dashboard_rows(self, user_id: UUID) -> List[Tuple[Evaluation, Job]]:
        statement = (
            select(Evaluation, Job)
            .join(Job, Job.id == Evaluation.job_id)
            .where(Evaluation.user_id == user_id)
            .order_by(Evaluation.updated_at.desc())
        )
        return list(self.session.exec(statement).all())

    def serialize_dashboard_rows(self, user_id: UUID) -> List[Dict[str, object]]:
        rows = self.list_dashboard_rows(user_id)
        payload: List[Dict[str, object]] = []
        for evaluation, job in rows:
            payload.append(
                {
                    "evaluation_id": evaluation.id,
                    "status": evaluation.status,
                    "fit_score": evaluation.fit_score,
                    "reasoning": evaluation.reasoning,
                    "user_feedback": evaluation.user_feedback,
                    "feedback_reason": evaluation.feedback_reason,
                    "job": job,
                }
            )
        return payload
