import { readFile } from "fs/promises";
import path from "path";

export type InternalLinkItem = {
  label: string;
  url: string;
};

export type InternalStatusDocument = {
  updatedAt: string | null;
  currentFocus: string[];
  milestones: string[];
  actions: string[];
  backlog: string[];
  notes: string[];
  references: InternalLinkItem[];
};

export type PromptOpsDocumentSummary = {
  updatedAt: string | null;
  family: string;
  snapshotItems: string[];
  interpretation: string[];
  usageNotes: string[];
  referenceLinks: InternalLinkItem[];
};

export async function loadInternalStatusDocument(): Promise<InternalStatusDocument> {
  const markdown = await readDocsMarkdown("internal/status.md");

  return {
    updatedAt: extractDocumentDate(markdown),
    currentFocus: extractBulletItems(extractSection(markdown, "현재 작업 중")),
    milestones: extractBulletItems(extractSection(markdown, "프로젝트 milestone 및 진행상황")),
    actions: extractBulletItems(extractSection(markdown, "지금 해야 할 action")),
    backlog: extractBulletItems(extractSection(markdown, "앞으로의 backlog")),
    notes: extractBulletItems(extractSection(markdown, "운영 메모")),
    references: extractLinkItems(extractSection(markdown, "참고 링크")),
  };
}

export async function loadPromptOpsDocumentSummary(): Promise<PromptOpsDocumentSummary> {
  const markdown = await readDocsMarkdown("promptops/status.md");
  const family = extractFirstFamilyHeading(markdown) ?? "job-evaluation";

  return {
    updatedAt: extractDocumentDate(markdown),
    family,
    snapshotItems: extractBulletItems(extractSection(markdown, "현재 상태 스냅샷")),
    interpretation: extractBulletItems(extractSection(markdown, "현재 해석")),
    usageNotes: extractNumberedItems(extractSection(markdown, "역할별 사용법")),
    referenceLinks: extractLinkItems(extractSection(markdown, "LangSmith / 문서 / Notion 링크")),
  };
}

async function readDocsMarkdown(relativePath: string): Promise<string> {
  const docsPath = path.resolve(process.cwd(), "..", "..", "docs", relativePath);
  return readFile(docsPath, "utf-8");
}

function extractDocumentDate(markdown: string): string | null {
  const match = markdown.match(/^(?:날짜|Date):\s*(.+)$/m);
  return match?.[1]?.trim() || null;
}

function extractFirstFamilyHeading(markdown: string): string | null {
  const lines = markdown.split(/\r?\n/);
  for (const line of lines) {
    const match = line.match(/^##\s+`?([^`]+?)`?\s*$/);
    if (match) {
      return match[1].trim();
    }
  }

  return null;
}

function extractSection(markdown: string, heading: string): string {
  const lines = markdown.split(/\r?\n/);
  const normalizedHeading = normalizeHeading(heading);
  let startIndex = -1;
  let headingLevel = 0;

  for (let index = 0; index < lines.length; index += 1) {
    const line = lines[index];
    const match = line.match(/^(#{2,6})\s+(.+?)\s*$/);
    if (!match) {
      continue;
    }

    const [, hashes, rawHeading] = match;
    if (normalizeHeading(rawHeading) === normalizedHeading) {
      startIndex = index + 1;
      headingLevel = hashes.length;
      break;
    }
  }

  if (startIndex < 0) {
    return "";
  }

  const sectionLines: string[] = [];
  for (let index = startIndex; index < lines.length; index += 1) {
    const line = lines[index];
    const match = line.match(/^(#{2,6})\s+(.+?)\s*$/);
    if (match && match[1].length <= headingLevel) {
      break;
    }
    sectionLines.push(line);
  }

  return sectionLines.join("\n").trim();
}

function normalizeHeading(value: string): string {
  return value.replace(/`/g, "").trim().toLowerCase();
}

function extractBulletItems(section: string): string[] {
  if (!section) {
    return [];
  }

  return section
    .split(/\r?\n/)
    .map((line) => line.match(/^\s*-\s+(.+)$/)?.[1]?.trim() ?? null)
    .filter((line): line is string => Boolean(line))
    .map(stripInlineMarkdown);
}

function extractNumberedItems(section: string): string[] {
  if (!section) {
    return [];
  }

  return section
    .split(/\r?\n/)
    .map((line) => line.match(/^\s*\d+\.\s+(.+)$/)?.[1]?.trim() ?? null)
    .filter((line): line is string => Boolean(line))
    .map(stripInlineMarkdown);
}

function extractLinkItems(section: string): InternalLinkItem[] {
  if (!section) {
    return [];
  }

  const items: InternalLinkItem[] = [];

  for (const rawLine of section.split(/\r?\n/)) {
    const line = rawLine.match(/^\s*-\s+(.+)$/)?.[1]?.trim();
    if (!line) {
      continue;
    }

    const linkMatch = line.match(/\[([^\]]+)\]\(([^)]+)\)/);
    if (!linkMatch) {
      continue;
    }

    const [, linkLabel, url] = linkMatch;
    const label = stripInlineMarkdown(line).replace(/\s+/g, " ").trim();
    items.push({
      label: label.length > 0 ? label : linkLabel.trim(),
      url: url.trim(),
    });
  }

  return items;
}

function stripInlineMarkdown(value: string): string {
  return value
    .replace(/\[([^\]]+)\]\([^)]+\)/g, "$1")
    .replace(/`([^`]+)`/g, "$1")
    .replace(/\*\*([^*]+)\*\*/g, "$1")
    .replace(/\*([^*]+)\*/g, "$1")
    .trim();
}
