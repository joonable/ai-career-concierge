from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from common.ids import generate_run_id


@dataclass(frozen=True)
class TraceContext:
    run_id: str
    started_at: datetime


def start_trace_context() -> TraceContext:
    return TraceContext(
        run_id=generate_run_id(),
        started_at=datetime.now(timezone.utc),
    )
