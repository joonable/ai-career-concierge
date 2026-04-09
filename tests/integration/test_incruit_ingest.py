from sqlmodel import select
from tests.conftest import FakeJobStore, FakeSystemLogStore, seed_user

from agent.nodes.ingest_node import IngestNode
from db.models import Job
from scraper.sources.incruit.scraper import IncruitScraper

LISTING_HTML = """
<section class="jobs">
  <article class="job-card" data-job-id="1001">
    <a class="job-title" href="/job/1001">Senior Machine Learning Engineer</a>
    <span class="company-name">Signal Labs</span>
    <span class="career">5~8년</span>
  </article>
  <article class="job-card" data-job-id="discard-me">
    <a class="job-title" href="/job/discard-me">Incomplete Posting</a>
    <span class="company-name">Signal Labs</span>
  </article>
</section>
"""

VALID_DETAIL_HTML = """
<html>
  <head>
    <link rel="canonical" href="https://job.incruit.com/job/1001?job=1001" />
  </head>
  <body>
    <section class="job-description" data-job-id="1001">
      Build recommendation systems with Python, SQL, online inference systems, and LLM evaluation workflows.
      Partner with product and platform teams to ship production ML features with measurable impact.
    </section>
    <div class="career-info">경력 5~8년</div>
  </body>
</html>
"""

INVALID_DETAIL_HTML = """
<html>
  <body>
    <section class="job-description" data-job-id="discard-me">short text</section>
  </body>
</html>
"""


class FixtureIncruitScraper(IncruitScraper):
    def __init__(self) -> None:
        super().__init__(max_pages=1, base_url="https://job.incruit.com")

    async def _fetch_search_html(self, *, keyword: str, page: int) -> str:
        del keyword
        del page
        return LISTING_HTML

    async def _fetch_detail_html(self, detail_url: str) -> str:
        if "discard-me" in detail_url:
            return INVALID_DETAIL_HTML
        return VALID_DETAIL_HTML


async def test_incruit_ingest_upserts_jobs_and_discards_invalid_entries(db_session):
    user = seed_user(db_session)
    node = IngestNode(
        scraper_registry=type("Registry", (), {"sources": [FixtureIncruitScraper()]})(),
        job_store=FakeJobStore(db_session),
        system_log_store=FakeSystemLogStore(db_session),
    )

    state = {
        "run_id": "run-1",
        "user_context": {
            "user_id": str(user.id),
            "profile_data": user.profile_data,
        },
    }

    first_result = await node.run(state)
    second_result = await node.run(state)

    assert len(first_result["current_jobs"]) == 1
    assert len(second_result["current_jobs"]) == 1

    jobs = db_session.exec(select(Job)).all()
    assert len(jobs) == 1
    assert jobs[0].external_job_id == "1001"
    assert jobs[0].min_years_experience == 5
    assert jobs[0].max_years_experience == 8


async def test_incruit_scraper_partial_parse_failure_does_not_fail_source(db_session):
    user = seed_user(db_session)
    scraper = FixtureIncruitScraper()

    jobs = await scraper.fetch_jobs(
        {
            "user_id": str(user.id),
            "profile_data": user.profile_data,
        }
    )

    assert len(jobs) == 1
    assert jobs[0].title == "Senior Machine Learning Engineer"
