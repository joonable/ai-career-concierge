from __future__ import annotations

from collections.abc import Iterable
from typing import List

from scraper.base import BaseScraperSource


class ScraperRegistry:
    def __init__(self, sources: Iterable[BaseScraperSource]):
        self._sources = list(sources)

    @property
    def sources(self) -> List[BaseScraperSource]:
        return list(self._sources)
