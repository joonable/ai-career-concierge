from __future__ import annotations

from typing import Any, Dict, Optional
from uuid import UUID

from sqlmodel import Session, select

from db.enums import LogLevel
from db.models import SystemLog


class SystemLogRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(
        self,
        *,
        run_id: str,
        event_type: str,
        message: str,
        level: LogLevel = LogLevel.INFO,
        user_id: Optional[UUID] = None,
        job_id: Optional[UUID] = None,
        platform: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> SystemLog:
        log = SystemLog(
            run_id=run_id,
            event_type=event_type,
            level=level,
            message=message,
            user_id=user_id,
            job_id=job_id,
            platform=platform,
            event_metadata=metadata or {},
        )
        self.session.add(log)
        self.session.commit()
        self.session.refresh(log)
        return log

    def list_for_run(self, run_id: str):
        statement = select(SystemLog).where(SystemLog.run_id == run_id)
        return list(self.session.exec(statement).all())
