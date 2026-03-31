import { readFile } from "fs/promises";
import path from "path";

export type InternalLinkItem = {
  label: string;
  url: string;
};

export type InternalStatusDocument = {
  updatedAt: string | null;
  operationsAgent: string[];
  userProductUX: string[];
  milestones: string[];
  actions: string[];
  recentCompletions: string[];
  backlog: string[];
  notes: string[];
  references: InternalLinkItem[];
  coreDocuments: InternalLinkItem[];
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
  const statusMarkdown = await readDocsMarkdown("internal/status.md");

  return {
    updatedAt: extractDocumentDate(statusMarkdown),
    operationsAgent: extractBulletItems(extractSection(statusMarkdown, "시스템 및 에이전트 관점 (Operations & Agent)")),
    userProductUX: extractBulletItems(extractSection(statusMarkdown, "유저 및 제품 관점 (User & Product UX)")),
    milestones: extractBulletItems(extractSection(statusMarkdown, "프로젝트 milestone 및 진행상황")),
    actions: extractBulletItems(extractSection(statusMarkdown, "다음 action")),
    recentCompletions: extractBulletItems(extractSection(statusMarkdown, "최근 완료 작업 (Done)")),
    backlog: extractBulletItems(extractSection(statusMarkdown, "backlog")),
    notes: extractBulletItems(extractSection(statusMarkdown, "운영 메모")),
    references: extractLinkItems(extractSection(statusMarkdown, "핵심 문서 및 참고 링크")),
    coreDocuments: extractLinkItems(extractSection(statusMarkdown, "핵심 문서 및 참고 링크")),
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
    
    let processedUrl = url.trim();
    if (processedUrl.endsWith('.md') && !processedUrl.startsWith('http')) {
      const cleanPath = processedUrl.replace(/^(\.\.\/|\.\/)+/, '');
      processedUrl = `/internal/docs/${cleanPath}`;
    }

    const label = stripInlineMarkdown(line).replace(/\s+/g, " ").trim();
    items.push({
      label: label.length > 0 ? label : linkLabel.trim(),
      url: processedUrl,
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
