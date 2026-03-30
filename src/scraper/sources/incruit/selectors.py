from __future__ import annotations

from urllib.parse import urlencode


SOURCE_NAME = "incruit"
DEFAULT_BASE_URL = "https://job.incruit.com"
LIST_PATH = "/jobdb_list/searchjob.asp"

LISTING_CARD_HINTS = ("data-job-id", "job", "recruit", "posting", "position")
TITLE_HINTS = ("title", "tit", "job", "position")
COMPANY_HINTS = ("company", "corp", "cpname", "name")
EXPERIENCE_HINTS = ("career", "experience", "exp", "year")
DETAIL_HINTS = ("job", "description", "detail", "content", "summary")

DETAIL_ID_QUERY_KEYS = (
    "job",
    "jk",
    "jobid",
    "job_id",
    "jobno",
    "postingid",
    "recruitno",
)


def build_search_url(*, base_url: str, keyword: str, page: int) -> str:
    query = urlencode({"kw": keyword, "page": page})
    return f"{base_url.rstrip('/')}{LIST_PATH}?{query}"
