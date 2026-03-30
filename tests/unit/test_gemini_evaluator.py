import httpx
import pytest

from api.services.gemini_evaluator import GeminiEvaluator


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
