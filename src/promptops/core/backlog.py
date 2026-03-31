from __future__ import annotations

from promptops.core.models import BacklogItem, FailureRecord


PRIORITY_BY_CATEGORY = {
    "policy": "P0",
    "feature": "P1",
    "prompt": "P1",
    "context": "P1",
    "dataset": "P2",
}


def backlog_priority_for_category(category: str) -> str:
    """Return the default backlog priority for a failure category."""

    return PRIORITY_BY_CATEGORY.get(category, "P2")


def build_backlog_item(
    *,
    item_key: str,
    category: str,
    title: str,
    action: str,
    linked_failures: list[FailureRecord] | None = None,
) -> BacklogItem:
    """Build an actionable backlog item from one or more failure records."""

    linked_failures = linked_failures or []
    return BacklogItem(
        item_key=item_key,
        category=category,
        priority=backlog_priority_for_category(category),
        title=title,
        action=action,
        linked_taxonomy_keys=[failure.taxonomy_key for failure in linked_failures],
        evidence=[evidence for failure in linked_failures for evidence in failure.evidence],
    )
