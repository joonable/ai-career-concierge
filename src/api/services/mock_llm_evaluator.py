from __future__ import annotations

from typing import Any, Dict, List, Optional


class MockGeminiEvaluator:
    async def evaluate(
        self,
        *,
        job,
        prompt: str,
        user_context: Dict[str, Any],
        recent_memory: str,
        prompt_metadata: Optional[Dict[str, Any]] = None,
        evaluation_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        del prompt
        del recent_memory
        del prompt_metadata
        del evaluation_id

        text = f"{job.title} {job.jd_raw_text}".lower()
        guidelines = user_context.get("guidelines", {})
        must_haves: List[str] = guidelines.get("must_haves", [])
        deal_breakers: List[str] = guidelines.get("deal_breakers", [])

        must_have_hits = [item for item in must_haves if item.lower() in text]
        deal_breakers_found = [item for item in deal_breakers if item.lower() in text]

        fit_score = 60 + (len(must_have_hits) * 15) - (len(deal_breakers_found) * 25)
        if "machine learning" in text or "ml" in text:
            fit_score += 10
        if "senior" in job.title.lower():
            fit_score += 5

        fit_score = max(1, min(100, fit_score))
        reasoning_bits = must_have_hits[:2] or ["profile fit inferred from title and description"]
        if deal_breakers_found:
            reasoning_bits.append(f"watch-outs: {', '.join(deal_breakers_found[:2])}")
        concerns = [f"deal-breaker: {item}" for item in deal_breakers_found]
        if not concerns and "contract" in text:
            concerns.append("contract terms need review")
        strengths = [f"matched: {item}" for item in must_have_hits[:3]]
        if "machine learning" in text or "ml" in text:
            strengths.append("ml scope is explicit in the role")

        confidence = "LOW"
        if fit_score >= 85 and len(must_have_hits) >= 2 and not deal_breakers_found:
            confidence = "HIGH"
        elif fit_score >= 60:
            confidence = "MEDIUM"

        role_alignment = "LOW"
        if "machine learning" in text or "ml" in text:
            role_alignment = "HIGH" if "engineer" in text else "MEDIUM"

        must_have_coverage = "WEAK"
        if len(must_have_hits) >= max(2, len(must_haves)):
            must_have_coverage = "STRONG"
        elif must_have_hits:
            must_have_coverage = "PARTIAL"

        deal_breaker_severity = "HARD" if deal_breakers_found else "NONE"

        transferable_skills = "LOW"
        if must_have_hits:
            transferable_skills = "HIGH" if len(must_have_hits) >= 2 else "MEDIUM"

        return {
            "fit_score": fit_score,
            "summary": " / ".join(reasoning_bits),
            "strengths": strengths,
            "concerns": concerns,
            "must_have_matches": must_have_hits,
            "deal_breaker_flags": deal_breakers_found,
            "confidence": confidence,
            "role_alignment": role_alignment,
            "must_have_coverage": must_have_coverage,
            "deal_breaker_severity": deal_breaker_severity,
            "transferable_skills": transferable_skills,
        }
