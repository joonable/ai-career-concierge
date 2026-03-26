from __future__ import annotations

from typing import Any, Dict

from agent.schemas.pipeline_job import PipelineJob


def build_evaluation_prompt(
    user_context: Dict[str, Any],
    recent_memory: str,
    job: PipelineJob,
) -> str:
    profile_data = user_context.get("profile_data", {})
    guidelines = user_context.get("guidelines", {})
    must_haves = ", ".join(guidelines.get("must_haves", [])) or "None provided"
    deal_breakers = ", ".join(guidelines.get("deal_breakers", [])) or "None provided"

    return (
        "You are evaluating whether a job is a strong match for one user.\n"
        f"Target role: {profile_data.get('role', 'unknown')}\n"
        f"Years of experience: {profile_data.get('years_of_experience', 'unknown')}\n"
        f"Must-haves: {must_haves}\n"
        f"Deal-breakers: {deal_breakers}\n"
        f"Recent dislike memory: {recent_memory or 'No recent dislike memory.'}\n"
        f"Job title: {job.title}\n"
        f"Company: {job.company}\n"
        f"Job description: {job.jd_raw_text}\n"
        "Return JSON with fit_score, reasoning, must_have_hits, and deal_breakers_found."
    )
