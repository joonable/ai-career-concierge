from __future__ import annotations

from enum import Enum


class EvaluationStatus(str, Enum):
    PENDING = "PENDING"
    RULE_REJECTED = "RULE_REJECTED"
    LLM_EVALUATED = "LLM_EVALUATED"


class FeedbackState(str, Enum):
    LIKE = "LIKE"
    DISLIKE = "DISLIKE"


class LogLevel(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
