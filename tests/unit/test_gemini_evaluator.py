import httpx
import pytest
from contextlib import contextmanager

from api.services.gemini_evaluator import GeminiEvaluator


class RecordingRunHandle:
    def __init__(self) -> None:
        self.outputs = None
        self.metadata = {}

    def set_outputs(self, outputs):
        self.outputs = outputs

    def add_metadata(self, metadata):
        self.metadata.update(metadata)


class RecordingTracer:
    def __init__(self) -> None:
        self.calls = []
        self.handles = []

    @contextmanager
    def llm_run(self, *, name, inputs, metadata, tags):
        handle = RecordingRunHandle()
        self.calls.append(
            {
                "name": name,
                "inputs": inputs,
                "metadata": metadata,
                "tags": tags,
            }
        )
        self.handles.append(handle)
        yield handle


@pytest.mark.asyncio
async def test_gemini_evaluator_maps_valid_json_response():
    def handler(request: httpx.Request) -> httpx.Response:
        assert "generateContent" in str(request.url)
        return httpx.Response(
            200,
            json={
                "candidates": [
                    {
                        "content": {
                            "parts": [
                                {
                                    "text": (
                                        '{"fit_score": 88, "reasoning": "Strong platform fit\\n'
                                        'Matches core stack", "must_have_hits": ["Python"], '
                                        '"deal_breakers_found": []}'
                                    )
                                }
                            ]
                        }
                    }
                ]
            },
        )

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    evaluator = GeminiEvaluator(api_key="test-key", http_client=client)

    result = await evaluator.evaluate(
        job=None,
        prompt="prompt",
        user_context={},
        recent_memory="",
    )

    assert result["fit_score"] == 88
    assert result["must_have_hits"] == ["Python"]
    assert result["_provider_metadata"]["model"] == "gemini-2.0-flash"
    await client.aclose()


@pytest.mark.asyncio
async def test_gemini_evaluator_rejects_non_json_text():
    def handler(request: httpx.Request) -> httpx.Response:
        del request
        return httpx.Response(
            200,
            json={
                "candidates": [
                    {"content": {"parts": [{"text": "not json"}]}}
                ]
            },
        )

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    evaluator = GeminiEvaluator(api_key="test-key", http_client=client)

    with pytest.raises(ValueError, match="valid JSON"):
        await evaluator.evaluate(job=None, prompt="prompt", user_context={}, recent_memory="")

    await client.aclose()


@pytest.mark.asyncio
async def test_gemini_evaluator_raises_runtime_error_for_http_failures():
    def handler(request: httpx.Request) -> httpx.Response:
        del request
        return httpx.Response(500, json={"error": {"message": "boom"}})

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    evaluator = GeminiEvaluator(api_key="test-key", http_client=client)

    with pytest.raises(RuntimeError, match="Gemini request failed"):
        await evaluator.evaluate(job=None, prompt="prompt", user_context={}, recent_memory="")

    await client.aclose()


@pytest.mark.asyncio
async def test_gemini_evaluator_traces_sanitized_inputs_and_outputs():
    def handler(request: httpx.Request) -> httpx.Response:
        del request
        return httpx.Response(
            200,
            json={
                "candidates": [
                    {
                        "content": {
                            "parts": [
                                {
                                    "text": (
                                        '{"fit_score": 88, "reasoning": "Strong platform fit\\n'
                                        'Matches core stack", "must_have_hits": ["Python"], '
                                        '"deal_breakers_found": []}'
                                    )
                                }
                            ]
                        }
                    }
                ]
            },
        )

    class Job:
        job_id = "job-1"
        external_job_id = "external-1"
        platform = "linkedin"
        title = "Senior ML Engineer"
        company = "Signal Labs"
        url = "https://example.com/jobs/1"

    tracer = RecordingTracer()
    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    evaluator = GeminiEvaluator(api_key="test-key", http_client=client, tracer=tracer)

    result = await evaluator.evaluate(
        job=Job(),
        prompt="prompt-body",
        user_context={
            "user_id": "user-1",
            "email": "secret@example.com",
            "profile_data": {"role": "ML Engineer", "years_of_experience": 6},
            "notification_settings": {"minimum_fit_score": 82},
        },
        recent_memory="avoid onsite-heavy roles",
    )

    assert result["fit_score"] == 88
    assert len(tracer.calls) == 1
    trace_call = tracer.calls[0]
    assert trace_call["name"] == "gemini.evaluate"
    assert trace_call["inputs"]["prompt"] == "prompt-body"
    assert trace_call["inputs"]["user_context"] == {
        "user_id": "user-1",
        "role": "ML Engineer",
        "years_of_experience": 6,
        "minimum_fit_score": 82,
    }
    assert "email" not in str(trace_call["inputs"])
    assert trace_call["metadata"]["external_job_id"] == "external-1"
    assert tracer.handles[0].outputs["parsed_payload"]["fit_score"] == 88
    assert tracer.handles[0].metadata["model"] == "gemini-2.0-flash"
    assert "latency_ms" in tracer.handles[0].metadata
    await client.aclose()
