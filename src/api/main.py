from __future__ import annotations

from fastapi import FastAPI

from api.routes.evaluations import router as evaluation_router
from api.routes.pipeline import router as pipeline_router
from api.routes.slack import router as slack_router
from api.routes.users import router as users_router
from common.config import get_settings
from common.logging import configure_logging


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings.app_debug)

    application = FastAPI(title="AI Career Concierge API", version="0.1.0")
    application.include_router(pipeline_router)
    application.include_router(slack_router)
    application.include_router(users_router)
    application.include_router(evaluation_router)

    @application.get("/")
    def root():
        return {
            "name": "AI Career Concierge API",
            "status": "ok",
            "docs_url": "/docs",
            "healthcheck_url": "/healthz",
        }

    @application.get("/healthz")
    def healthcheck():
        return {"ok": True, "env": settings.app_env.value}

    return application


app = create_app()
