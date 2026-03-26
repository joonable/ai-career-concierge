from __future__ import annotations

from typing import Any, Dict, List

from scraper.base import ScrapedJob


class MockPlatformScraper:
    source_name = "mock_platform"

    async def fetch_jobs(self, user_context: Dict[str, Any]) -> List[ScrapedJob]:
        return [
            ScrapedJob(
                platform=self.source_name,
                external_job_id="mock-001",
                title="Senior Machine Learning Engineer",
                company="Signal Labs",
                jd_raw_text=(
                    "Build ranking and recommendation systems with Python, SQL, and LLM "
                    "evaluation workflows. Experience with production ML systems is required."
                ),
                url="https://example.com/jobs/mock-001",
                min_years_experience=4,
                max_years_experience=8,
                source_metadata={"location": "Seoul", "employment_type": "Full-time"},
            ),
            ScrapedJob(
                platform=self.source_name,
                external_job_id="mock-002",
                title="Junior Frontend Engineer",
                company="Noise Portal",
                jd_raw_text="Maintain a marketing site with minimal backend exposure.",
                url="https://example.com/jobs/mock-002",
                min_years_experience=0,
                max_years_experience=2,
                source_metadata={"location": "Remote", "employment_type": "Contract"},
            ),
        ]
