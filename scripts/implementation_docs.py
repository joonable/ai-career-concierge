#!/usr/bin/env python3

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
import unicodedata
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

ACTIVE_ROOT = Path("docs/implementation/active")
ARCHIVE_ROOT = Path("docs/implementation/archive")
TODO_PATH = Path("TODO.md")
MILESTONE_PATH = Path("MILESTONE.md")
PROPOSED_PLAN_RE = re.compile(r"<proposed_plan>\s*(.*?)\s*</proposed_plan>", re.DOTALL)
DIRNAME_RE = re.compile(r"^\d{4}-\d{2}-\d{2}-[0-9a-z가-힣-]+$")
FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n?", re.DOTALL)
MANAGED_BLOCK_RE_TEMPLATE = r"(<!-- BEGIN MANAGED:{name} -->\n)(.*?)(\n<!-- END MANAGED:{name} -->)"
SPLIT_LENGTH_THRESHOLD = 4000
SPLIT_SECTION_THRESHOLD = 4
FRONTMATTER_KEYS = (
    "plan_id",
    "title",
    "status",
    "milestone",
    "source_agent",
    "created_at",
    "updated_at",
)


@dataclass
class Section:
    heading: str
    body: str


@dataclass
class PlanPackage:
    package_dir: Path
    index_path: Path
    metadata: dict[str, str]
    body: str

    @property
    def plan_id(self) -> str:
        return self.metadata["plan_id"]

    @property
    def title(self) -> str:
        return self.metadata["title"]

    @property
    def milestone(self) -> str:
        return self.metadata["milestone"]

    @property
    def status(self) -> str:
        return self.metadata["status"]

    @property
    def source_agent(self) -> str:
        return self.metadata["source_agent"]

    @property
    def created_at(self) -> str:
        return self.metadata["created_at"]

    @property
    def updated_at(self) -> str:
        return self.metadata["updated_at"]


def now_iso() -> str:
    return datetime.now().astimezone().replace(microsecond=0).isoformat()


def slugify(value: str) -> str:
    lowered = unicodedata.normalize("NFKC", value).lower()
    lowered = re.sub(r"[^0-9a-z가-힣]+", "-", lowered)
    lowered = re.sub(r"-{2,}", "-", lowered)
    lowered = lowered.strip("-")
    if lowered:
        return lowered
    digest = hashlib.sha1(value.encode("utf-8")).hexdigest()[:8]
    return f"plan-{digest}"


def repo_root_from_script() -> Path:
    return Path(__file__).resolve().parent.parent


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def split_frontmatter(text: str) -> tuple[dict[str, str], str]:
    match = FRONTMATTER_RE.match(text)
    if not match:
        return {}, text

    raw_frontmatter = match.group(1)
    metadata: dict[str, str] = {}
    for line in raw_frontmatter.splitlines():
        if not line.strip():
            continue
        key, sep, value = line.partition(":")
        if not sep:
            raise ValueError(f"Invalid frontmatter line: {line}")
        metadata[key.strip()] = value.strip()
    return metadata, text[match.end() :]


def compose_frontmatter(metadata: dict[str, str]) -> str:
    missing = [key for key in FRONTMATTER_KEYS if key not in metadata or not metadata[key].strip()]
    if missing:
        raise ValueError(f"Missing frontmatter keys: {', '.join(missing)}")

    lines = ["---"]
    for key in FRONTMATTER_KEYS:
        lines.append(f"{key}: {metadata[key]}")
    lines.append("---")
    return "\n".join(lines)


def parse_title_and_sections(markdown: str) -> tuple[str, str, list[Section]]:
    normalized = markdown.strip()
    if not normalized:
        raise ValueError("Plan markdown is empty.")

    lines = normalized.splitlines()
    if lines[0].startswith("# "):
        title = lines[0][2:].strip()
        remainder = "\n".join(lines[1:]).lstrip()
    else:
        title = lines[0].strip()
        remainder = "\n".join(lines[1:]).lstrip()
        if remainder:
            remainder = f"{remainder}"

    matches = list(re.finditer(r"(?m)^##\s+(.+?)\n", remainder))
    if not matches:
        return title, remainder.strip(), []

    intro = remainder[: matches[0].start()].strip()
    sections: list[Section] = []
    for index, match in enumerate(matches):
        heading = match.group(1).strip()
        start = match.start()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(remainder)
        section_text = remainder[start:end].strip()
        sections.append(Section(heading=heading, body=section_text))
    return title, intro, sections


def section_filename(index: int, heading: str, used: set[str]) -> str:
    normalized = heading.strip().lower()
    if normalized in {"summary", "요약", "개요", "목적"}:
        candidate = "01-summary.md"
    elif normalized in {"implementation", "implementation changes", "구현", "구현 변경"}:
        candidate = "02-implementation.md"
    elif normalized in {"test plan", "test", "테스트 계획"}:
        candidate = "03-test-plan.md"
    elif normalized in {"assumptions", "assumption", "가정", "기본 가정"}:
        candidate = "04-assumptions.md"
    else:
        ordinal = max(index, len(used) + 1)
        candidate = f"{ordinal:02d}-{slugify(heading)}.md"

    if candidate not in used:
        used.add(candidate)
        return candidate

    stem = candidate[:-3]
    suffix = 2
    while True:
        deduped = f"{stem}-{suffix:02d}.md"
        if deduped not in used:
            used.add(deduped)
            return deduped
        suffix += 1


def build_split_files(title: str, intro: str, sections: list[Section]) -> tuple[str, dict[str, str]]:
    prepared_sections: list[Section] = []
    intro_lines = [line.strip() for line in intro.splitlines() if line.strip()]
    keep_intro_as_section = len(intro_lines) > 1 or len(intro.strip()) > 120

    if intro.strip() and keep_intro_as_section:
        prepared_sections.append(Section(heading="요약", body=f"## 요약\n\n{intro.strip()}"))
    prepared_sections.extend(sections)

    used_filenames: set[str] = set()
    section_files: dict[str, str] = {}
    links: list[tuple[str, str]] = []
    for index, section in enumerate(prepared_sections, start=1):
        filename = section_filename(index, section.heading, used_filenames)
        heading = section.heading
        content = section.body.strip()
        if not content.startswith("## "):
            content = f"## {heading}\n\n{content}"
        section_files[filename] = content + "\n"
        links.append((heading, filename))

    index_lines = [f"# {title}", ""]
    if intro.strip():
        index_lines.extend([intro.strip(), ""])
    index_lines.extend(["## 문서 구성", ""])
    for heading, filename in links:
        index_lines.append(f"- [{heading}]({filename})")
    index_lines.append("")
    return "\n".join(index_lines), section_files


def should_split(markdown: str, section_count: int) -> bool:
    return len(markdown) > SPLIT_LENGTH_THRESHOLD or section_count > SPLIT_SECTION_THRESHOLD


def extract_plan_markdown(raw_text: str) -> str | None:
    match = PROPOSED_PLAN_RE.search(raw_text)
    if not match:
        return None
    return match.group(1).strip()


def extract_markdown_from_hook_payload(payload: dict[str, Any], hook_event: str | None) -> str | None:
    ordered_candidates: list[str] = []
    if hook_event == "Stop":
        ordered_candidates.append(str(payload.get("last_assistant_message", "")))
    elif hook_event == "AfterAgent":
        ordered_candidates.append(str(payload.get("prompt_response", "")))

    ordered_candidates.extend(
        [
            str(payload.get("last_assistant_message", "")),
            str(payload.get("prompt_response", "")),
            str(payload.get("response", "")),
        ]
    )

    for candidate in ordered_candidates:
        if not candidate.strip():
            continue
        extracted = extract_plan_markdown(candidate)
        if extracted:
            return extracted
    return None


def load_markdown_from_args(args: argparse.Namespace) -> str | None:
    if args.source_file:
        return read_text(Path(args.source_file))

    stdin_text = ""
    if args.stdin_json or args.stdin_markdown or not sys.stdin.isatty():
        stdin_text = sys.stdin.read()

    if args.stdin_json:
        payload = json.loads(stdin_text)
        return extract_markdown_from_hook_payload(payload, args.hook_event)

    if args.stdin_markdown:
        return stdin_text.strip() or None

    if stdin_text.strip():
        extracted = extract_plan_markdown(stdin_text)
        return extracted or stdin_text.strip()
    return None


def relative_to_root(path: Path, repo_root: Path) -> str:
    return path.relative_to(repo_root).as_posix()


def parse_datetime_sort_key(value: str) -> tuple[int, str]:
    try:
        return (0, datetime.fromisoformat(value).astimezone().isoformat())
    except ValueError:
        return (1, value)


def scan_plan_packages(repo_root: Path) -> list[PlanPackage]:
    packages: list[PlanPackage] = []
    active_root = repo_root / ACTIVE_ROOT
    archive_root = repo_root / ARCHIVE_ROOT

    candidate_indexes = list(active_root.glob("*/index.md")) + list(archive_root.glob("*/*/index.md"))
    for index_path in candidate_indexes:
        metadata, body = split_frontmatter(read_text(index_path))
        packages.append(PlanPackage(package_dir=index_path.parent, index_path=index_path, metadata=metadata, body=body))
    return packages


def milestone_sort_key(value: str) -> tuple[int, int | str, str]:
    match = re.match(r"^Phase\s+(\d+)", value)
    if match:
        return (0, int(match.group(1)), value)
    if value.lower() == "backlog":
        return (1, 999, value)
    return (2, value, value)


def build_todo_managed_block(
    repo_root: Path, active_packages: list[PlanPackage], archived_packages: list[PlanPackage]
) -> str:
    active_packages = sorted(
        active_packages,
        key=lambda package: parse_datetime_sort_key(package.updated_at),
        reverse=True,
    )
    archived_packages = sorted(
        archived_packages,
        key=lambda package: parse_datetime_sort_key(package.updated_at),
        reverse=True,
    )
    lines = ["## Active Plans", ""]
    if active_packages:
        for package in active_packages:
            rel = relative_to_root(package.index_path, repo_root)
            lines.append(
                f"- [{package.title}]({rel})"
                f" — milestone: `{package.milestone}`, agent: `{package.source_agent}`, updated: `{package.updated_at}`"
            )
    else:
        lines.append("- 현재 활성 plan package 없음")

    lines.extend(["", "## Priority Snapshot", ""])
    counter = Counter(package.milestone for package in active_packages)
    if counter:
        for milestone, count in sorted(counter.items(), key=lambda item: milestone_sort_key(item[0])):
            lines.append(f"- `{milestone}`: active {count}건")
    else:
        lines.append("- active plan 없음")

    lines.extend(["", "## Recent Archive", ""])
    archived_sorted = sorted(
        archived_packages,
        key=lambda package: parse_datetime_sort_key(package.updated_at),
        reverse=True,
    )
    if archived_sorted:
        for package in archived_sorted[:5]:
            rel = relative_to_root(package.index_path, repo_root)
            lines.append(f"- [{package.title}]({rel}) — `{package.updated_at}`")
    else:
        lines.append("- 최근 archive 없음")
    return "\n".join(lines)


def build_milestone_managed_block(
    repo_root: Path, active_packages: list[PlanPackage], archived_packages: list[PlanPackage]
) -> str:
    active_packages = sorted(
        active_packages,
        key=lambda package: parse_datetime_sort_key(package.updated_at),
        reverse=True,
    )
    archived_packages = sorted(
        archived_packages,
        key=lambda package: parse_datetime_sort_key(package.updated_at),
        reverse=True,
    )
    active_grouped: dict[str, list[PlanPackage]] = defaultdict(list)
    for package in active_packages:
        active_grouped[package.milestone].append(package)

    lines = ["## Active By Milestone", ""]
    if active_grouped:
        for milestone in sorted(active_grouped, key=milestone_sort_key):
            lines.append(f"### {milestone}")
            lines.append("")
            for package in sorted(
                active_grouped[milestone],
                key=lambda item: parse_datetime_sort_key(item.updated_at),
                reverse=True,
            ):
                rel = relative_to_root(package.index_path, repo_root)
                lines.append(f"- [{package.title}]({rel}) — `{package.updated_at}`")
            lines.append("")
    else:
        lines.extend(["- 현재 active plan 없음", ""])

    lines.extend(["## History Timeline", ""])
    archive_grouped: dict[str, list[PlanPackage]] = defaultdict(list)
    for package in archived_packages:
        archive_grouped[package.package_dir.parent.name].append(package)

    if archive_grouped:
        for year in sorted(archive_grouped.keys(), reverse=True):
            lines.append(f"### {year}")
            lines.append("")
            for package in sorted(
                archive_grouped[year],
                key=lambda item: parse_datetime_sort_key(item.updated_at),
                reverse=True,
            ):
                rel = relative_to_root(package.index_path, repo_root)
                lines.append(f"- [{package.title}]({rel}) — `{package.milestone}` / `{package.updated_at}`")
            lines.append("")
    else:
        lines.extend(["- archive history 없음", ""])
    return "\n".join(lines).rstrip()


def replace_managed_block(text: str, name: str, content: str) -> str:
    pattern = re.compile(MANAGED_BLOCK_RE_TEMPLATE.format(name=re.escape(name)), re.DOTALL)
    replacement = rf"\1{content}\3"
    updated, count = pattern.subn(replacement, text)
    if count != 1:
        raise ValueError(f"Managed block {name} not found or duplicated.")
    return updated


def sync_indexes(repo_root: Path) -> None:
    packages = scan_plan_packages(repo_root)
    active_packages = sorted(
        [package for package in packages if package.status == "active"],
        key=lambda package: parse_datetime_sort_key(package.updated_at),
        reverse=True,
    )
    archived_packages = sorted(
        [package for package in packages if package.status == "archived"],
        key=lambda package: parse_datetime_sort_key(package.updated_at),
        reverse=True,
    )

    todo_content = build_todo_managed_block(repo_root, active_packages, archived_packages)
    milestone_content = build_milestone_managed_block(repo_root, active_packages, archived_packages)

    todo_path = repo_root / TODO_PATH
    milestone_path = repo_root / MILESTONE_PATH
    write_text(todo_path, replace_managed_block(read_text(todo_path), "IMPLEMENTATION_INDEX", todo_content))
    write_text(
        milestone_path,
        replace_managed_block(read_text(milestone_path), "MILESTONE_INDEX", milestone_content),
    )


def package_dir_for(active_root: Path, timestamp: str, slug: str) -> Path:
    date_part = datetime.fromisoformat(timestamp).date().isoformat()
    return active_root / f"{date_part}-{slug}"


def update_metadata(
    existing: dict[str, str] | None,
    *,
    title: str,
    status: str,
    milestone: str,
    source_agent: str,
    created_at: str | None = None,
    updated_at: str | None = None,
    package_name: str,
) -> dict[str, str]:
    base = dict(existing or {})
    base["plan_id"] = base.get("plan_id") or package_name
    base["title"] = title
    base["status"] = status
    base["milestone"] = milestone
    base["source_agent"] = source_agent
    base["created_at"] = created_at or base.get("created_at") or now_iso()
    base["updated_at"] = updated_at or now_iso()
    return base


def clear_package_markdown_files(package_dir: Path) -> None:
    if not package_dir.exists():
        return
    for markdown_file in package_dir.glob("*.md"):
        markdown_file.unlink()


def save_plan(args: argparse.Namespace) -> Path | None:
    repo_root = Path(args.repo_root).resolve()
    markdown = load_markdown_from_args(args)
    if not markdown:
        return None

    title, intro, sections = parse_title_and_sections(markdown)
    slug = args.slug or slugify(args.title or title)
    created_at = args.created_at or now_iso()
    package_dir = package_dir_for(repo_root / ACTIVE_ROOT, created_at, slug)
    existing_metadata: dict[str, str] | None = None
    if (package_dir / "index.md").exists():
        existing_metadata, _ = split_frontmatter(read_text(package_dir / "index.md"))

    metadata = update_metadata(
        existing_metadata,
        title=args.title or title,
        status="active",
        milestone=args.milestone,
        source_agent=args.agent,
        created_at=args.created_at,
        updated_at=args.updated_at,
        package_name=package_dir.name,
    )

    clear_package_markdown_files(package_dir)

    if should_split(markdown, len(sections)):
        index_body, section_files = build_split_files(args.title or title, intro, sections)
        write_text(package_dir / "index.md", f"{compose_frontmatter(metadata)}\n{index_body}")
        for filename, content in section_files.items():
            write_text(package_dir / filename, content)
    else:
        body = markdown.strip()
        write_text(package_dir / "index.md", f"{compose_frontmatter(metadata)}\n{body}")

    if args.sync:
        sync_indexes(repo_root)

    return package_dir


def resolve_active_package(repo_root: Path, identifier: str) -> PlanPackage:
    active_packages = [package for package in scan_plan_packages(repo_root) if package.status == "active"]
    for package in active_packages:
        if identifier in {package.plan_id, package.package_dir.name, package.title}:
            return package
    raise ValueError(f"Active plan not found: {identifier}")


def archive_plan(args: argparse.Namespace) -> Path:
    repo_root = Path(args.repo_root).resolve()
    package = resolve_active_package(repo_root, args.identifier)
    archived_at = args.updated_at or now_iso()
    archive_year = datetime.fromisoformat(archived_at).date().strftime("%Y")
    target_dir = repo_root / ARCHIVE_ROOT / archive_year / package.package_dir.name
    if target_dir.exists():
        raise ValueError(f"Archive target already exists: {target_dir}")

    target_dir.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(package.package_dir), str(target_dir))

    index_path = target_dir / "index.md"
    metadata, body = split_frontmatter(read_text(index_path))
    metadata = update_metadata(
        metadata,
        title=metadata["title"],
        status="archived",
        milestone=metadata["milestone"],
        source_agent=metadata["source_agent"],
        updated_at=archived_at,
        package_name=target_dir.name,
    )
    write_text(index_path, f"{compose_frontmatter(metadata)}\n{body.strip()}")

    if args.sync:
        sync_indexes(repo_root)
    return target_dir


def validate(repo_root: Path) -> None:
    todo_text = read_text(repo_root / TODO_PATH)
    milestone_text = read_text(repo_root / MILESTONE_PATH)
    if (
        "<!-- BEGIN MANAGED:IMPLEMENTATION_INDEX -->" not in todo_text
        or "<!-- END MANAGED:IMPLEMENTATION_INDEX -->" not in todo_text
    ):
        raise ValueError("TODO.md managed block is missing.")
    if (
        "<!-- BEGIN MANAGED:MILESTONE_INDEX -->" not in milestone_text
        or "<!-- END MANAGED:MILESTONE_INDEX -->" not in milestone_text
    ):
        raise ValueError("MILESTONE.md managed block is missing.")

    packages = scan_plan_packages(repo_root)
    if not packages:
        raise ValueError("No plan packages found under docs/implementation.")

    seen_plan_ids: set[str] = set()
    for package in packages:
        dirname = package.package_dir.name
        if not DIRNAME_RE.match(dirname):
            raise ValueError(f"Invalid plan package directory name: {dirname}")
        for key in FRONTMATTER_KEYS:
            if key not in package.metadata or not package.metadata[key].strip():
                raise ValueError(f"Missing frontmatter key {key} in {package.index_path}")
        if package.plan_id in seen_plan_ids:
            raise ValueError(f"Duplicate plan_id found: {package.plan_id}")
        seen_plan_ids.add(package.plan_id)

        if package.status == "active":
            expected_prefix = repo_root / ACTIVE_ROOT
        elif package.status == "reference":
            expected_prefix = repo_root / ACTIVE_ROOT
        elif package.status == "archived":
            expected_prefix = repo_root / ARCHIVE_ROOT
        else:
            raise ValueError(f"Invalid status {package.status} in {package.index_path}")

        if expected_prefix not in package.index_path.parents:
            raise ValueError(f"Status/path mismatch for {package.index_path}")

        metadata, body = split_frontmatter(read_text(package.index_path))
        if not body.strip():
            raise ValueError(f"Plan body is empty: {package.index_path}")
        if metadata["title"] not in body:
            raise ValueError(f"Title not reflected in body: {package.index_path}")

    expected_todo = replace_managed_block(
        todo_text,
        "IMPLEMENTATION_INDEX",
        build_todo_managed_block(
            repo_root,
            [package for package in packages if package.status == "active"],
            [package for package in packages if package.status == "archived"],
        ),
    )
    if expected_todo != todo_text:
        raise ValueError("TODO.md managed block is out of sync.")

    expected_milestone = replace_managed_block(
        milestone_text,
        "MILESTONE_INDEX",
        build_milestone_managed_block(
            repo_root,
            [package for package in packages if package.status == "active"],
            [package for package in packages if package.status == "archived"],
        ),
    )
    if expected_milestone != milestone_text:
        raise ValueError("MILESTONE.md managed block is out of sync.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Manage implementation plan packages.")
    parser.add_argument("--repo-root", default=str(repo_root_from_script()), help="Repository root path")
    subparsers = parser.add_subparsers(dest="command", required=True)

    save_parser = subparsers.add_parser("save-plan", help="Save a plan package to docs/implementation/active")
    save_parser.add_argument("--agent", required=True, help="Agent name")
    save_parser.add_argument("--milestone", default="Backlog", help="Milestone label")
    save_parser.add_argument("--title", help="Optional title override")
    save_parser.add_argument("--slug", help="Optional slug override")
    save_parser.add_argument("--source-file", help="Read markdown from a file")
    save_parser.add_argument("--created-at", help="ISO timestamp override")
    save_parser.add_argument("--updated-at", help="ISO timestamp override")
    save_parser.add_argument("--hook-event", choices=["Stop", "AfterAgent"], help="Hook event name")
    save_parser.add_argument("--stdin-json", action="store_true", help="Read hook JSON from stdin")
    save_parser.add_argument("--stdin-markdown", action="store_true", help="Read markdown from stdin")
    save_parser.add_argument("--sync", action="store_true", default=True, help="Sync TODO/MILESTONE after save")
    save_parser.add_argument("--no-sync", action="store_false", dest="sync", help="Skip index sync")
    save_parser.add_argument("--quiet", action="store_true", help="Suppress stdout output")

    archive_parser = subparsers.add_parser("archive-plan", help="Archive an active plan package")
    archive_parser.add_argument("identifier", help="plan_id, package directory, or exact title")
    archive_parser.add_argument("--updated-at", help="ISO timestamp override")
    archive_parser.add_argument("--sync", action="store_true", default=True, help="Sync TODO/MILESTONE after archive")
    archive_parser.add_argument("--no-sync", action="store_false", dest="sync", help="Skip index sync")
    archive_parser.add_argument("--quiet", action="store_true", help="Suppress stdout output")

    sync_parser = subparsers.add_parser("sync-indexes", help="Refresh TODO/MILESTONE managed blocks")
    sync_parser.add_argument("--quiet", action="store_true", help="Suppress stdout output")

    validate_parser = subparsers.add_parser("validate", help="Validate naming, metadata, and managed blocks")
    validate_parser.add_argument("--quiet", action="store_true", help="Suppress stdout output")

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    repo_root = Path(args.repo_root).resolve()
    try:
        if args.command == "save-plan":
            package_dir = save_plan(args)
            if package_dir is not None and not args.quiet:
                print(relative_to_root(package_dir, repo_root))
        elif args.command == "archive-plan":
            target_dir = archive_plan(args)
            if not args.quiet:
                print(relative_to_root(target_dir, repo_root))
        elif args.command == "sync-indexes":
            sync_indexes(repo_root)
            if not args.quiet:
                print("synced")
        elif args.command == "validate":
            validate(repo_root)
            if not args.quiet:
                print("ok")
        else:
            raise ValueError(f"Unsupported command: {args.command}")
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
