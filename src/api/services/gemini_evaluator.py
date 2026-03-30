from __future__ import annotations

import json
import time
from typing import Any, Dict, Optional

import httpx


class GeminiEvaluator:
    def __init__(
        self,
        *,
        api_key: str,
        model: str = "gemini-2.0-flash",
        base_url: str = "https://generativelanguage.googleapis.com/v1beta",
        timeout_seconds: float = 30.0,
        http_client: Optional[httpx.AsyncClient] = None,
    ) -> None:
        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds
        self._http_client = http_client

    async def evaluate(
        self,
        *,
        job,
        prompt: str,
        user_context: Dict[str, Any],
        recent_memory: str,
    ) -> Dict[str, Any]:
        del job
        del user_context
        del recent_memory

        started_at = time.perf_counter()
        response_payload = await self._post_generate_content(prompt=prompt)
        response_text = self._extract_text_response(response_payload)
        parsed_payload = self._parse_json_response(response_text)
        parsed_payload["_provider_metadata"] = {
            "model": self.model,
            "latency_ms": int((time.perf_counter() - started_at) * 1000),
        }
        return parsed_payload

    async def _post_generate_content(self, *, prompt: str) -> Dict[str, Any]:
        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": prompt}],
                }
            ],
            "generationConfig": {
                "temperature": 0.2,
                "responseMimeType": "application/json",
            },
        }
        owned_client = self._http_client is None
        client = self._http_client or httpx.AsyncClient(timeout=self.timeout_seconds)
        try:
            response = await client.post(
                f"{self.base_url}/models/{self.model}:generateContent",
                params={"key": self.api_key},
                json=payload,
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as exc:
            raise RuntimeError(f"Gemini request failed: {exc}") from exc
        finally:
            if owned_client:
                await client.aclose()

    @staticmethod
    def _extract_text_response(payload: Dict[str, Any]) -> str:
        candidates = payload.get("candidates") or []
        if not candidates:
            raise ValueError("Gemini response did not include candidates.")

        parts = ((candidates[0].get("content") or {}).get("parts")) or []
        text_chunks = [part.get("text", "") for part in parts if isinstance(part, dict)]
        text = "\n".join(chunk for chunk in text_chunks if chunk).strip()
        if not text:
            raise ValueError("Gemini response did not include text content.")
        return GeminiEvaluator._strip_code_fences(text)

    @staticmethod
    def _strip_code_fences(text: str) -> str:
        stripped = text.strip()
        if stripped.startswith("```") and stripped.endswith("```"):
            lines = stripped.splitlines()
            if len(lines) >= 3:
                return "\n".join(lines[1:-1]).strip()
        return stripped

    @staticmethod
    def _parse_json_response(text: str) -> Dict[str, Any]:
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError as exc:
            raise ValueError("Gemini response was not valid JSON.") from exc

        if not isinstance(parsed, dict):
            raise ValueError("Gemini response JSON must be an object.")
        return parsed
