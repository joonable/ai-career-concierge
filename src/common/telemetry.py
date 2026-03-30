from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Generator, Optional

from common.ids import generate_run_id

try:  # pragma: no cover - import guard only
    from langsmith import Client
    from langsmith.run_helpers import get_current_run_tree, tracing_context
    from langsmith.run_trees import RunTree
except ImportError:  # pragma: no cover - local env fallback
    Client = None
    RunTree = None
    get_current_run_tree = None
    tracing_context = None


@dataclass(frozen=True)
class TraceContext:
    run_id: str
    started_at: datetime


def start_trace_context() -> TraceContext:
    return TraceContext(
        run_id=generate_run_id(),
        started_at=datetime.now(timezone.utc),
    )


@dataclass
class LangSmithRunHandle:
    run_tree: Optional[Any] = None
    outputs: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self) -> None:
        if self.metadata is None:
            self.metadata = {}

    @property
    def enabled(self) -> bool:
        return self.run_tree is not None

    def set_outputs(self, outputs: Dict[str, Any]) -> None:
        self.outputs = outputs

    def add_metadata(self, metadata: Dict[str, Any]) -> None:
        self.metadata.update(metadata)

    def end_success(self) -> None:
        if self.run_tree is None:
            return
        self.run_tree.end(
            outputs=self.outputs,
            metadata=self.metadata or None,
        )

    def end_error(self, exc: Exception) -> None:
        if self.run_tree is None:
            return
        self.run_tree.end(
            error=f"{exc.__class__.__name__}: {exc}",
            metadata=self.metadata or None,
        )


class LangSmithTracer:
    def __init__(
        self,
        *,
        enabled: bool,
        project_name: str = "",
        app_env: str = "",
        client: Optional[Any] = None,
    ) -> None:
        self.enabled = enabled
        self.project_name = project_name
        self.app_env = app_env
        self.client = client

    @classmethod
    def disabled(cls) -> "LangSmithTracer":
        return cls(enabled=False)

    @classmethod
    def from_settings(cls, settings: Any) -> "LangSmithTracer":
        if not settings.langsmith_api_key or Client is None or RunTree is None or tracing_context is None:
            return cls.disabled()

        return cls(
            enabled=True,
            project_name=settings.langsmith_project,
            app_env=settings.app_env.value,
            client=Client(api_key=settings.langsmith_api_key),
        )

    @contextmanager
    def pipeline_run(
        self,
        *,
        run_id: str,
        user_id: str,
        dry_run: bool,
        app_env: str,
    ) -> Generator[LangSmithRunHandle, None, None]:
        if not self.enabled or RunTree is None or tracing_context is None:
            yield LangSmithRunHandle()
            return

        metadata = {
            "run_id": run_id,
            "user_id": user_id,
            "dry_run": dry_run,
            "app_env": app_env,
            "pipeline_trigger": True,
        }
        root_run = RunTree(
            name="pipeline.trigger",
            run_type="chain",
            project_name=self.project_name,
            inputs={
                "run_id": run_id,
                "user_id": user_id,
                "dry_run": dry_run,
            },
            tags=["pipeline_trigger", f"env:{app_env}"],
            extra={"metadata": metadata},
            ls_client=self.client,
        )
        self._post_run(root_run)
        handle = LangSmithRunHandle(run_tree=root_run)

        with tracing_context(
            parent=root_run,
            enabled=True,
            client=self.client,
            project_name=self.project_name,
            tags=["pipeline_trigger", f"env:{app_env}"],
            metadata=metadata,
        ):
            try:
                yield handle
            except Exception as exc:
                handle.add_metadata({"error_type": exc.__class__.__name__})
                handle.end_error(exc)
                raise
            else:
                handle.end_success()
            finally:
                self._patch_run(root_run)

    @contextmanager
    def llm_run(
        self,
        *,
        name: str,
        inputs: Dict[str, Any],
        metadata: Dict[str, Any],
        tags: Optional[list[str]] = None,
    ) -> Generator[LangSmithRunHandle, None, None]:
        if not self.enabled or RunTree is None or get_current_run_tree is None:
            yield LangSmithRunHandle()
            return

        parent_run = get_current_run_tree()
        if parent_run is None:
            yield LangSmithRunHandle()
            return

        child_run = parent_run.create_child(
            name=name,
            run_type="llm",
            inputs=inputs,
            tags=tags or ["llm_eval"],
            extra={"metadata": metadata},
        )
        self._post_run(child_run)
        handle = LangSmithRunHandle(run_tree=child_run)

        try:
            yield handle
        except Exception as exc:
            handle.add_metadata({"error_type": exc.__class__.__name__})
            handle.end_error(exc)
            raise
        else:
            handle.end_success()
        finally:
            self._patch_run(child_run)

    def _post_run(self, run_tree: Any) -> None:
        run_tree.post()

    def _patch_run(self, run_tree: Any) -> None:
        run_tree.patch()
