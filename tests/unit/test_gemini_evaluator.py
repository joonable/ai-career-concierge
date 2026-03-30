import httpx
import pytest

from api.services.gemini_evaluator import GeminiEvaluator
from common.errors import ProviderRequestError, ProviderResponseParseError


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
                                        '{"fit_score": 88, "summary": "Strong platform fit\\n'
                                        'Matches core stack", "strengths": ["Python match"], '
                                        '"concerns": ["Need infra scope confirmation"], '
                                        '"must_have_matches": ["Python"], '
                                        '"deal_breaker_flags": [], "confidence": "MEDIUM"}'
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
    assert result["must_have_matches"] == ["Python"]
    assert result["_provider_metadata"]["model"] == "gemini-2.0-flash"
    assert "Strong platform fit" in result["_raw_response_text"]
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

    with pytest.raises(ProviderResponseParseError, match="valid JSON"):
        await evaluator.evaluate(job=None, prompt="prompt", user_context={}, recent_memory="")

    await client.aclose()


@pytest.mark.asyncio
async def test_gemini_evaluator_raises_provider_error_for_http_failures():
    def handler(request: httpx.Request) -> httpx.Response:
        del request
        return httpx.Response(500, json={"error": {"message": "boom"}})

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    evaluator = GeminiEvaluator(api_key="test-key", http_client=client)

    with pytest.raises(ProviderRequestError, match="Gemini request failed"):
        await evaluator.evaluate(job=None, prompt="prompt", user_context={}, recent_memory="")

    await client.aclose()
