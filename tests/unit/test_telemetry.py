from __future__ import annotations

from contextlib import contextmanager

import pytest

from common.telemetry import LangSmithTracer


class FakeRunTree:
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.children = []
        self.posted = False
        self.patched = False
        self.ended_with = {}

    def create_child(self, **kwargs):
        child = FakeRunTree(**kwargs)
        self.children.append(child)
        return child

    def post(self):
        self.posted = True

    def end(self, **kwargs):
        self.ended_with = kwargs

    def patch(self):
        self.patched = True


@contextmanager
def passthrough_tracing_context(**kwargs):
    del kwargs
    yield


def test_langsmith_tracer_records_pipeline_outputs(monkeypatch):
    import common.telemetry as telemetry_module

    monkeypatch.setattr(telemetry_module, "RunTree", FakeRunTree)
    monkeypatch.setattr(telemetry_module, "tracing_context", passthrough_tracing_context)

    tracer = LangSmithTracer(enabled=True, project_name="proj", app_env="development", client=object())

    with tracer.pipeline_run(
        run_id="run-1",
        user_id="user-1",
        dry_run=False,
        app_env="development",
    ) as handle:
        handle.set_outputs({"jobs_ingested": 2, "jobs_sent": 1})

    assert handle.enabled is True
    assert handle.run_tree.posted is True
    assert handle.run_tree.patched is True
    assert handle.run_tree.ended_with["outputs"] == {"jobs_ingested": 2, "jobs_sent": 1}
    assert handle.run_tree.kwargs["extra"]["metadata"]["run_id"] == "run-1"


def test_langsmith_tracer_records_llm_error_metadata(monkeypatch):
    import common.telemetry as telemetry_module

    parent_run = FakeRunTree(name="parent")
    monkeypatch.setattr(telemetry_module, "get_current_run_tree", lambda: parent_run)

    tracer = LangSmithTracer(enabled=True, project_name="proj", app_env="development", client=object())

    with pytest.raises(ValueError, match="boom"):
        with tracer.llm_run(
            name="gemini.evaluate",
            inputs={"prompt": "hello"},
            metadata={"job_id": "job-1"},
            tags=["llm_eval"],
        ) as handle:
            handle.add_metadata({"model": "gemini-2.0-flash"})
            raise ValueError("boom")

    child = parent_run.children[0]
    assert child.posted is True
    assert child.patched is True
    assert child.ended_with["error"] == "ValueError: boom"
    assert child.ended_with["metadata"]["error_type"] == "ValueError"
    assert child.ended_with["metadata"]["model"] == "gemini-2.0-flash"
