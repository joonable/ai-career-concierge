from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy import Enum as SQLEnum
from sqlmodel import Field, SQLModel

from db.enums import EvaluationStatus, FeedbackState


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Evaluation(SQLModel, table=True):
    """
    프로젝트 데이터 모델 중 가장 핵심이 되는 '사용자별 채용 공고 평가 결과' 엔티티입니다.
    User와 Job 사이를 다대다(N:M) 관계로 이어주는 조인 테이블(Join Table) 역할을 겸합니다.

    저장 정보:
    - 상태 전이: PENDING(대기) -> RULE_REJECTED(규칙 탈락) -> LLM_EVALUATED(LLM 완료)
    - LLM 평가 결과: 적합도 점수(fit_score) 및 세부 이유(reasoning)
    - 사용자 피드백: 좋아요/싫어요(user_feedback) 이력 (단기 기억 갱신용)
    """

    __tablename__ = "evaluations"
    __table_args__ = (UniqueConstraint("user_id", "job_id", name="uq_evaluations_user_job"),)

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(sa_column=Column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True))
    job_id: uuid.UUID = Field(sa_column=Column(ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True))
    status: EvaluationStatus = Field(
        default=EvaluationStatus.PENDING,
        sa_column=Column(
            SQLEnum(EvaluationStatus, native_enum=False, length=32),
            nullable=False,
            default=EvaluationStatus.PENDING,
        ),
    )
    fit_score: Optional[int] = Field(default=None, sa_column=Column(Integer, nullable=True))
    reasoning: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    rule_rejection_reason: Optional[str] = Field(default=None, sa_column=Column(String(255), nullable=True))
    user_feedback: Optional[FeedbackState] = Field(
        default=None,
        sa_column=Column(SQLEnum(FeedbackState, native_enum=False, length=16), nullable=True),
    )
    feedback_reason: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    created_at: datetime = Field(
        default_factory=utc_now,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    updated_at: datetime = Field(
        default_factory=utc_now,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
