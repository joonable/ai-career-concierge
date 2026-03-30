from __future__ import annotations

import json
import time
from typing import Any, Dict, Optional

import httpx

from common.telemetry import LangSmithTracer


class GeminiEvaluator:
    def __init__(
        self,
        *,
        api_key: str,
        model: str = "gemini-2.0-flash",
        base_url: str = "https://generativelanguage.googleapis.com/v1beta",
        timeout_seconds: float = 30.0,
        http_client: Optional[httpx.AsyncClient] = None,
        tracer: Optional[LangSmithTracer] = None,
    ) -> None:
        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds
        self._http_client = http_client
        self.tracer = tracer or LangSmithTracer.disabled()

    async def evaluate(
        self,
        *,
        job,
        prompt: str,
        user_context: Dict[str, Any],
        recent_memory: str,
    ) -> Dict[str, Any]:
        trace_inputs = self._build_trace_inputs(
            job=job,
            prompt=prompt,
            user_context=user_context,
            recent_memory=recent_memory,
        )
        trace_metadata = {
            "job_id": str(getattr(job, "job_id", "")),
            "external_job_id": getattr(job, "external_job_id", ""),
            "platform": getattr(job, "platform", "unknown"),
            "title": getattr(job, "title", ""),
            "model": self.model,
        }

        with self.tracer.llm_run(
            name="gemini.evaluate",
            inputs=trace_inputs,
            metadata=trace_metadata,
            tags=["llm_eval", f"platform:{getattr(job, 'platform', 'unknown')}", f"model:{self.model}"],
        ) as llm_trace:
            started_at = time.perf_counter()
            response_payload = await self._post_generate_content(prompt=prompt)
            response_text = self._extract_text_response(response_payload)
            parsed_payload = self._parse_json_response(response_text)
            provider_metadata = {
                "model": self.model,
                "latency_ms": int((time.perf_counter() - started_at) * 1000),
            }
            parsed_payload["_provider_metadata"] = provider_metadata
            llm_trace.set_outputs(
                {
                    "response_text": response_text,
                    "parsed_payload": parsed_payload,
                }
            )
            llm_trace.add_metadata(provider_metadata)
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

    @staticmethod
    def _build_trace_inputs(
        *,
        job,
        prompt: str,
        user_context: Dict[str, Any],
        recent_memory: str,
    ) -> Dict[str, Any]:
        profile_data = user_context.get("profile_data", {})
        notification_settings = user_context.get("notification_settings", {})

        return {
            "prompt": prompt,
            "job": {
                "job_id": str(getattr(job, "job_id", "")),
                "external_job_id": getattr(job, "external_job_id", ""),
                "platform": getattr(job, "platform", "unknown"),
                "title": getattr(job, "title", ""),
                "company": getattr(job, "company", ""),
                "url": getattr(job, "url", ""),
            },
            "user_context": {
                "user_id": str(user_context.get("user_id", "")),
                "role": profile_data.get("role", ""),
                "years_of_experience": profile_data.get("years_of_experience"),
                "minimum_fit_score": notification_settings.get("minimum_fit_score"),
            },
            "recent_memory": recent_memory,
        }
