from scraper.base import ScrapedJob
from scraper.normalizers.job_normalizer import InvalidScrapedJobError, normalize_scraped_job
from scraper.sources.incruit.parsers import (
    extract_external_job_id,
    parse_detail_page,
    parse_experience_years,
    parse_listing_page,
)
from scraper.sources.incruit.selectors import build_search_url


LISTING_HTML = """
<section class="jobs">
  <article class="job-card" data-job-id="1001">
    <a class="job-title" href="/job/1001">
      Senior Machine Learning Engineer
    </a>
    <span class="company-name">Signal Labs</span>
    <span class="career">5~8년</span>
  </article>
  <article class="job-card" data-job-id="1002">
    <a class="job-title" href="/job/1002">
      Applied Scientist
    </a>
    <span class="company-name">Vector Works</span>
    <span class="career">3년 이상</span>
  </article>
</section>
"""

LISTING_HTML_FROM_INCRUIT = """
<div class="cBbslist_contenst">
  <ul class="c_row" jobno="2603090000132">
    <li class="c_col">
      <div class="cell_first">
        <div class="cl_top">
          <a href="https://www.incruit.com/company/1682190468" class="cpname" target="_blank">(주)버즈빌</a>
        </div>
      </div>
      <div class="cell_mid">
        <div class="cl_top">
          <a target="_blank" href="https://job.incruit.com/jobdb_info/jobpost.asp?job=2603090000132&src=gsw*etc">Machine Learning Engineer, Ads & Recommendation</a>
        </div>
        <div class="cl_md">
          <span>경력 3~8년</span>
        </div>
      </div>
    </li>
  </ul>
</div>
"""

DETAIL_HTML = """
<html>
  <head>
    <link rel="canonical" href="https://job.incruit.com/job/1001?job=1001" />
  </head>
  <body>
    <section class="job-description" data-job-id="1001">
      Build recommendation systems with Python, SQL, feature stores, and LLM evaluation workflows.
      Own production model deployment and experimentation pipelines across ranking surfaces.
    </section>
    <div class="career-info">경력 5~8년</div>
  </body>
</html>
"""

DETAIL_HTML_WITH_JSON_LD = """
<html>
  <head>
    <link rel="canonical" href="https://job.incruit.com/jobdb_info/jobpost.asp?job=2603230002546" />
    <script type="application/ld+json">
      {
        "@context": "http://schema.org/",
        "@type": "JobPosting",
        "title": "[디지털] AI Agent 개발 및 프로젝트 기획 담당자 채용",
        "description": "(주)신한디지털<br><br>AI Agent 개발 및 프로젝트 기획 담당자 채용<br>Python 기반의 AI 시스템을 설계하고 운영합니다.",
        "hiringOrganization": {
          "@type": "Organization",
          "name": "신한디지털"
        }
      }
    </script>
  </head>
  <body>
    <div class="career-info">경력 5년</div>
  </body>
</html>
"""


def test_build_search_url_includes_keyword_and_page():
    url = build_search_url(base_url="https://job.incruit.com", keyword="machine learning", page=2)

    assert url == "https://job.incruit.com/jobdb_list/searchjob.asp?kw=machine+learning&page=2"


def test_parse_listing_page_extracts_multiple_cards():
    previews = parse_listing_page(LISTING_HTML)

    assert len(previews) == 2
    assert previews[0].title == "Senior Machine Learning Engineer"
    assert previews[0].company == "Signal Labs"
    assert previews[0].detail_url == "/job/1001"
    assert previews[0].external_hint == "1001"


def test_parse_listing_page_extracts_real_incruit_card_shape():
    previews = parse_listing_page(LISTING_HTML_FROM_INCRUIT)

    assert len(previews) == 1
    assert previews[0].title == "Machine Learning Engineer, Ads & Recommendation"
    assert previews[0].company == "(주)버즈빌"
    assert previews[0].external_hint == "2603090000132"
    assert previews[0].detail_url.startswith("https://job.incruit.com/jobdb_info/jobpost.asp?job=2603090000132")


def test_parse_detail_page_extracts_job_description_and_identifier():
    detail = parse_detail_page(DETAIL_HTML, detail_url="/job/1001", hint="1001")

    assert "recommendation systems" in detail.jd_raw_text
    assert detail.external_job_id == "1001"
    assert detail.canonical_url == "https://job.incruit.com/job/1001?job=1001"
    assert detail.experience_text == "경력 5~8년"


def test_parse_detail_page_prefers_job_posting_json_ld_when_available():
    detail = parse_detail_page(
        DETAIL_HTML_WITH_JSON_LD,
        detail_url="https://job.incruit.com/jobdb_info/jobpost.asp?job=2603230002546",
        hint="",
    )

    assert detail.external_job_id == "2603230002546"
    assert detail.canonical_url == "https://job.incruit.com/jobdb_info/jobpost.asp?job=2603230002546"
    assert detail.company == "신한디지털"
    assert "Python 기반의 AI 시스템" in detail.jd_raw_text
    assert detail.title == "[디지털] AI Agent 개발 및 프로젝트 기획 담당자 채용"


def test_parse_experience_years_handles_ranges_and_minimums():
    assert parse_experience_years("5~8년") == (5, 8)
    assert parse_experience_years("3년 이상") == (3, None)
    assert parse_experience_years("7+ years of experience") == (7, None)
    assert parse_experience_years("경력 무관") == (None, None)


def test_extract_external_job_id_uses_query_path_and_hint_fallbacks():
    assert (
        extract_external_job_id(
            detail_url="https://job.incruit.com/job/1001?job=1001",
            canonical_url="",
            hint="",
        )
        == "1001"
    )
    assert extract_external_job_id(detail_url="https://job.incruit.com/job/position/7654", hint="") == "7654"
    assert extract_external_job_id(detail_url="https://job.incruit.com/job/detail", hint="4321") == "4321"


def test_normalize_scraped_job_builds_absolute_urls_and_rejects_short_jd():
    normalized = normalize_scraped_job(
        ScrapedJob(
            platform="incruit ",
            external_job_id=" 1001 ",
            title=" Senior   Machine Learning Engineer ",
            company=" Signal Labs ",
            jd_raw_text=(
                " Build recommendation systems with Python, SQL, experimentation, "
                "and LLM evaluation workflows in production. "
            ),
            url="/job/1001",
            source_metadata={"base_url": "https://job.incruit.com"},
        )
    )

    assert normalized.url == "https://job.incruit.com/job/1001"
    assert normalized.title == "Senior Machine Learning Engineer"

    try:
        normalize_scraped_job(
            ScrapedJob(
                platform="incruit",
                external_job_id="1002",
                title="Bad Job",
                company="Bad Company",
                jd_raw_text="too short",
                url="/job/1002",
                source_metadata={"base_url": "https://job.incruit.com"},
            )
        )
    except InvalidScrapedJobError as exc:
        assert "jd_raw_text" in str(exc)
    else:  # pragma: no cover - explicit assertion branch
        raise AssertionError("Expected InvalidScrapedJobError")
