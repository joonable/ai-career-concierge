from __future__ import annotations

import re
from dataclasses import dataclass
from html.parser import HTMLParser
from typing import Dict, List, Optional
from urllib.parse import parse_qs, urlparse

from scraper.sources.incruit.selectors import (
    COMPANY_HINTS,
    DETAIL_HINTS,
    DETAIL_ID_QUERY_KEYS,
    EXPERIENCE_HINTS,
    LISTING_CARD_HINTS,
    TITLE_HINTS,
)


WHITESPACE_RE = re.compile(r"\s+")
TAG_RE = re.compile(r"<[^>]+>")
PATH_ID_RE = re.compile(r"(\d{4,})")


def normalize_text(value: str) -> str:
    return WHITESPACE_RE.sub(" ", value).strip()


def strip_tags(value: str) -> str:
    return normalize_text(TAG_RE.sub(" ", value))


def class_matches(attrs: Dict[str, str], hints: tuple[str, ...]) -> bool:
    values = " ".join(
        [
            attrs.get("class", ""),
            attrs.get("id", ""),
            " ".join(attrs.keys()),
        ]
    ).lower()
    return any(hint in values for hint in hints)


def attrs_to_dict(attrs: List[tuple[str, Optional[str]]]) -> Dict[str, str]:
    return {key.lower(): (value or "") for key, value in attrs}


@dataclass
class ListingPreview:
    title: str
    company: str
    detail_url: str
    external_hint: str = ""
    experience_text: str = ""


@dataclass
class JobDetail:
    jd_raw_text: str
    external_job_id: str
    canonical_url: str = ""
    experience_text: str = ""


class _ListingParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.previews: List[ListingPreview] = []
        self._card_depth = 0
        self._current: Optional[dict] = None
        self._capture_title = False
        self._capture_company = False
        self._capture_experience = False

    def handle_starttag(self, tag: str, attrs: List[tuple[str, Optional[str]]]) -> None:
        attr_map = attrs_to_dict(attrs)
        if tag in {"article", "li", "div"} and (
            any(hint in attr_map for hint in ("data-job-id", "data-posting-id"))
            or class_matches(attr_map, LISTING_CARD_HINTS)
        ):
            if self._card_depth == 0:
                self._current = {
                    "title": "",
                    "company": "",
                    "detail_url": "",
                    "external_hint": attr_map.get("data-job-id")
                    or attr_map.get("data-posting-id")
                    or "",
                    "experience_text": "",
                }
            self._card_depth += 1

        if self._card_depth == 0 or self._current is None:
            return

        if tag == "a" and attr_map.get("href"):
            href = attr_map["href"]
            data_hint = (
                attr_map.get("data-job-id")
                or attr_map.get("data-posting-id")
                or self._current["external_hint"]
            )
            if not self._current["detail_url"] or class_matches(attr_map, TITLE_HINTS):
                self._current["detail_url"] = href
                self._current["external_hint"] = data_hint
                self._capture_title = True
            elif not self._current["title"]:
                self._current["detail_url"] = href
                self._capture_title = True

        if class_matches(attr_map, COMPANY_HINTS):
            self._capture_company = True

        if class_matches(attr_map, EXPERIENCE_HINTS):
            self._capture_experience = True

    def handle_endtag(self, tag: str) -> None:
        if tag == "a":
            self._capture_title = False

        self._capture_company = False
        self._capture_experience = False

        if self._card_depth > 0 and tag in {"article", "li", "div"}:
            self._card_depth -= 1
            if self._card_depth == 0 and self._current is not None:
                title = normalize_text(self._current["title"])
                company = normalize_text(self._current["company"])
                detail_url = self._current["detail_url"].strip()
                if title and company and detail_url:
                    self.previews.append(
                        ListingPreview(
                            title=title,
                            company=company,
                            detail_url=detail_url,
                            external_hint=self._current["external_hint"].strip(),
                            experience_text=normalize_text(self._current["experience_text"]),
                        )
                    )
                self._current = None

    def handle_data(self, data: str) -> None:
        if self._card_depth == 0 or self._current is None:
            return

        text = normalize_text(data)
        if not text:
            return

        if self._capture_title:
            self._current["title"] = f"{self._current['title']} {text}"
        if self._capture_company:
            self._current["company"] = f"{self._current['company']} {text}"
        if self._capture_experience:
            self._current["experience_text"] = f"{self._current['experience_text']} {text}"


class _DetailParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._capture_detail = False
        self._capture_experience = False
        self.detail_chunks: List[str] = []
        self.experience_chunks: List[str] = []
        self.canonical_url = ""
        self.external_hint = ""

    def handle_starttag(self, tag: str, attrs: List[tuple[str, Optional[str]]]) -> None:
        attr_map = attrs_to_dict(attrs)

        if tag == "link" and attr_map.get("rel", "").lower() == "canonical" and attr_map.get("href"):
            self.canonical_url = attr_map["href"]

        if tag == "meta" and attr_map.get("property", "").lower() == "og:url" and attr_map.get("content"):
            self.canonical_url = attr_map["content"]

        if any(key in attr_map for key in ("data-job-id", "data-posting-id")):
            self.external_hint = (
                attr_map.get("data-job-id") or attr_map.get("data-posting-id") or self.external_hint
            )

        if class_matches(attr_map, DETAIL_HINTS):
            self._capture_detail = True

        if class_matches(attr_map, EXPERIENCE_HINTS):
            self._capture_experience = True

    def handle_endtag(self, tag: str) -> None:
        del tag
        self._capture_detail = False
        self._capture_experience = False

    def handle_data(self, data: str) -> None:
        text = normalize_text(data)
        if not text:
            return
        if self._capture_detail:
            self.detail_chunks.append(text)
        if self._capture_experience:
            self.experience_chunks.append(text)


def parse_listing_page(html: str) -> List[ListingPreview]:
    parser = _ListingParser()
    parser.feed(html)
    return parser.previews


def extract_external_job_id(*, detail_url: str, canonical_url: str = "", hint: str = "") -> str:
    for candidate in (hint, canonical_url, detail_url):
        candidate = candidate.strip()
        if not candidate:
            continue
        if candidate.isdigit():
            return candidate

        parsed = urlparse(candidate)
        query_params = parse_qs(parsed.query)
        for key in DETAIL_ID_QUERY_KEYS:
            values = query_params.get(key, [])
            if values and values[0].strip():
                return values[0].strip()

        path_match = PATH_ID_RE.search(parsed.path or candidate)
        if path_match:
            return path_match.group(1)

    return ""


def parse_experience_years(raw_text: str) -> tuple[Optional[int], Optional[int]]:
    text = normalize_text(raw_text).lower()
    if not text:
        return None, None

    range_match = re.search(r"(\d+)\s*[~-]\s*(\d+)", text)
    if range_match:
        return int(range_match.group(1)), int(range_match.group(2))

    min_plus_match = re.search(r"(\d+)\s*\+|\b(\d+)\s*years?\s*\+", text)
    if min_plus_match:
        value = next(group for group in min_plus_match.groups() if group)
        return int(value), None

    korean_range = re.search(r"(\d+)\s*년\s*(?:이상)?\s*[~-]\s*(\d+)\s*년", text)
    if korean_range:
        return int(korean_range.group(1)), int(korean_range.group(2))

    korean_min = re.search(r"(\d+)\s*년\s*이상", text)
    if korean_min:
        return int(korean_min.group(1)), None

    english_min = re.search(r"(\d+)\s*(?:years?|yrs?)\s*(?:of experience)?", text)
    if english_min:
        return int(english_min.group(1)), None

    return None, None


def parse_detail_page(html: str, *, detail_url: str, hint: str = "") -> JobDetail:
    parser = _DetailParser()
    parser.feed(html)

    jd_raw_text = normalize_text(" ".join(parser.detail_chunks))
    experience_text = normalize_text(" ".join(parser.experience_chunks))
    canonical_url = parser.canonical_url.strip()
    external_job_id = extract_external_job_id(
        detail_url=detail_url,
        canonical_url=canonical_url,
        hint=parser.external_hint or hint,
    )

    return JobDetail(
        jd_raw_text=jd_raw_text,
        external_job_id=external_job_id,
        canonical_url=canonical_url,
        experience_text=experience_text,
    )
