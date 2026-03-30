"use client";

import React, { useState } from "react";

import type { DashboardRecommendation } from "@/lib/dashboard_mapper";

type RecommendationBoardProps = {
  minimumFitScore: number;
  recommendations: DashboardRecommendation[];
};

type SortOption = "latest" | "fit_desc" | "fit_asc";
type FeedbackFilter = "ALL" | "LIKE" | "DISLIKE" | "UNANSWERED";
type SavedView = "recommended" | "review" | "all";

export function RecommendationBoard({
  minimumFitScore,
  recommendations,
}: RecommendationBoardProps) {
  const [onlyQualified, setOnlyQualified] = useState(true);
  const [includeRejected, setIncludeRejected] = useState(false);
  const [sortOption, setSortOption] = useState<SortOption>("latest");
  const [feedbackFilter, setFeedbackFilter] = useState<FeedbackFilter>("ALL");
  const [savedView, setSavedView] = useState<SavedView>("recommended");
  const [platformFilter, setPlatformFilter] = useState("ALL");
  const [searchQuery, setSearchQuery] = useState("");

  const platformOptions = buildPlatformOptions(recommendations);
  const filteredRecommendations = filterRecommendations(recommendations, {
    minimumFitScore,
    onlyQualified,
    includeRejected,
    feedbackFilter,
    savedView,
    platformFilter,
    searchQuery,
  });
  const sortedRecommendations = sortRecommendations(filteredRecommendations, sortOption);
  const hasSourceRecommendations = recommendations.length > 0;

  return (
    <section className="dashboard-board">
      <div className="dashboard-section__header dashboard-section__header--responsive">
        <div>
          <span className="dashboard-kicker">Matches</span>
          <h2 className="dashboard-section__title">추천 목록</h2>
        </div>
        <div className="dashboard-board__summary">
          <p className="dashboard-meta">기준 {minimumFitScore}+ 추천 중심</p>
          <p className="dashboard-meta">
            {sortedRecommendations.length}개 표시 · 전체 {recommendations.length}개
          </p>
        </div>
      </div>

      <div className="dashboard-card dashboard-board__filter-panel">
        <div className="dashboard-board__filter-top">
          <label className="dashboard-search">
            <span className="dashboard-select__label">빠른 검색</span>
            <input
              aria-label="공고 검색"
              className="dashboard-search__input"
              onChange={(event) => setSearchQuery(event.target.value)}
              placeholder="회사명이나 직무명으로 찾기"
              type="search"
              value={searchQuery}
            />
          </label>
          <label className="dashboard-select dashboard-select--wide">
            <span className="dashboard-select__label">정렬</span>
            <select
              aria-label="공고 정렬 기준"
              onChange={(event) => setSortOption(event.target.value as SortOption)}
              value={sortOption}
            >
              <option value="latest">최신 공고</option>
              <option value="fit_desc">적합도 높은 순</option>
              <option value="fit_asc">적합도 낮은 순</option>
            </select>
          </label>
        </div>

        <div className="dashboard-filter-group">
          <span className="dashboard-select__label">저장 뷰</span>
          <div className="dashboard-segmented">
            <button
              className={buildSegmentClass(savedView === "recommended")}
              onClick={() => setSavedView("recommended")}
              type="button"
            >
              추천만
            </button>
            <button
              className={buildSegmentClass(savedView === "review")}
              onClick={() => setSavedView("review")}
              type="button"
            >
              검토 필요
            </button>
            <button
              className={buildSegmentClass(savedView === "all")}
              onClick={() => setSavedView("all")}
              type="button"
            >
              전체
            </button>
          </div>
        </div>

        <div className="dashboard-filter-grid">
          <div className="dashboard-filter-group">
            <span className="dashboard-select__label">빠른 조건</span>
            <div className="dashboard-toggle-list">
              <label className="dashboard-toggle dashboard-toggle--surface">
                <input
                  checked={onlyQualified}
                  onChange={(event) => setOnlyQualified(event.target.checked)}
                  type="checkbox"
                />
                <span>추천 기준 {minimumFitScore}점 이상만 보기</span>
              </label>
              <label className="dashboard-toggle dashboard-toggle--surface">
                <input
                  checked={includeRejected}
                  onChange={(event) => setIncludeRejected(event.target.checked)}
                  type="checkbox"
                />
                <span>규칙에서 제외된 공고도 포함</span>
              </label>
            </div>
          </div>

          <div className="dashboard-filter-group">
            <span className="dashboard-select__label">피드백 상태</span>
            <div className="dashboard-chip-filter-list">
              {[
                ["ALL", "전체"],
                ["UNANSWERED", "미응답"],
                ["LIKE", "좋아요"],
                ["DISLIKE", "싫어요"],
              ].map(([value, label]) => (
                <button
                  className={buildChipFilterClass(feedbackFilter === value)}
                  key={value}
                  onClick={() => setFeedbackFilter(value as FeedbackFilter)}
                  type="button"
                >
                  {label}
                </button>
              ))}
            </div>
          </div>
        </div>

        <div className="dashboard-filter-group">
          <span className="dashboard-select__label">플랫폼</span>
          <div className="dashboard-chip-filter-list">
            {platformOptions.map((platform) => (
              <button
                className={buildChipFilterClass(platformFilter === platform)}
                key={platform}
                onClick={() => setPlatformFilter(platform)}
                type="button"
              >
                {platform === "ALL" ? "전체" : platform}
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="dashboard-card-grid">
        {!hasSourceRecommendations ? (
          <article className="dashboard-card dashboard-card--full dashboard-empty-state">
            <span className="dashboard-kicker">Queue</span>
            <h3 className="dashboard-empty-state__title">아직 비어 있습니다</h3>
            <p className="dashboard-meta">파이프라인 실행 후 여기에 표시됩니다.</p>
          </article>
        ) : sortedRecommendations.length === 0 ? (
          <article className="dashboard-card dashboard-card--full dashboard-empty-state">
            <span className="dashboard-kicker">Filtered</span>
            <h3 className="dashboard-empty-state__title">현재 필터와 일치하는 공고가 없습니다</h3>
            <p className="dashboard-meta">
              검색어를 지우거나 저장 뷰, 플랫폼, 피드백 조건을 조금 완화해보세요.
            </p>
          </article>
        ) : (
          sortedRecommendations.map((recommendation) => (
            <article
              className="dashboard-card dashboard-card--interactive dashboard-recommendation"
              key={recommendation.evaluationId}
            >
              <div className="dashboard-recommendation__top">
                <div className="dashboard-score">
                  <strong>{recommendation.fitScore ?? "--"}</strong>
                  <span>{recommendation.fitScore === null ? "대기" : "적합도"}</span>
                </div>
                <span className="dashboard-pill">{recommendation.statusLabel}</span>
              </div>
              <div>
                <h3 className="dashboard-recommendation__title">{recommendation.title}</h3>
                <p className="dashboard-meta">
                  {recommendation.company} · {recommendation.platform}
                </p>
              </div>
              <div className="dashboard-chip-list">
                <span className="dashboard-chip">{recommendation.platform}</span>
                {recommendation.fitScore !== null && recommendation.fitScore >= minimumFitScore ? (
                  <span className="dashboard-chip dashboard-chip--success">기준 충족</span>
                ) : null}
                {recommendation.feedbackLabel ? (
                  <span className="dashboard-chip dashboard-chip--muted">
                    피드백 {recommendation.feedbackLabel}
                  </span>
                ) : (
                  <span className="dashboard-chip dashboard-chip--subtle">피드백 대기</span>
                )}
                {recommendation.ruleRejectionReason ? (
                  <span className="dashboard-chip dashboard-chip--warning">
                    제외 사유 {formatBadgeLabel(recommendation.ruleRejectionReason)}
                  </span>
                ) : null}
              </div>
              <p className="dashboard-recommendation__reasoning">
                {recommendation.reasoning ?? getFallbackReasoning(recommendation.status)}
              </p>
              {recommendation.feedbackReason ? (
                <p className="dashboard-recommendation__note">
                  최근 메모: {recommendation.feedbackReason}
                </p>
              ) : null}
              <div className="dashboard-recommendation__footer">
                <span className="dashboard-meta">
                  반영 시각 {formatRelativeDate(recommendation.updatedAt)}
                </span>
                <a
                  className="dashboard-link"
                  href={recommendation.url}
                  rel="noreferrer"
                  target="_blank"
                >
                  공고 보기
                </a>
              </div>
            </article>
          ))
        )}
      </div>
    </section>
  );
}

function filterRecommendations(
  recommendations: DashboardRecommendation[],
  filters: {
    minimumFitScore: number;
    onlyQualified: boolean;
    includeRejected: boolean;
    feedbackFilter: FeedbackFilter;
    savedView: SavedView;
    platformFilter: string;
    searchQuery: string;
  },
) {
  const normalizedQuery = filters.searchQuery.trim().toLowerCase();

  return recommendations.filter((recommendation) => {
    const isRejected = recommendation.status === "RULE_REJECTED";
    const isQualified =
      recommendation.status === "LLM_EVALUATED" &&
      recommendation.fitScore !== null &&
      recommendation.fitScore >= filters.minimumFitScore;
    const needsReview =
      recommendation.status === "PENDING" ||
      recommendation.userFeedback === null ||
      (recommendation.fitScore !== null && recommendation.fitScore < filters.minimumFitScore);

    if (filters.savedView === "recommended" && !isQualified && !(filters.includeRejected && isRejected)) {
      return false;
    }

    if (filters.savedView === "review" && !needsReview && !(filters.includeRejected && isRejected)) {
      return false;
    }

    if (filters.savedView === "all" && isRejected && !filters.includeRejected) {
      return false;
    }

    if (filters.onlyQualified && !isQualified && !(filters.includeRejected && isRejected)) {
      return false;
    }

    if (!filters.includeRejected && isRejected) {
      return false;
    }

    if (filters.feedbackFilter === "LIKE" && recommendation.userFeedback !== "LIKE") {
      return false;
    }
    if (filters.feedbackFilter === "DISLIKE" && recommendation.userFeedback !== "DISLIKE") {
      return false;
    }
    if (filters.feedbackFilter === "UNANSWERED" && recommendation.userFeedback !== null) {
      return false;
    }

    if (filters.platformFilter !== "ALL" && recommendation.platform !== filters.platformFilter) {
      return false;
    }

    if (!normalizedQuery) {
      return true;
    }

    const searchableText = `${recommendation.title} ${recommendation.company}`.toLowerCase();
    return searchableText.includes(normalizedQuery);
  });
}

function sortRecommendations(
  recommendations: DashboardRecommendation[],
  sortOption: SortOption,
) {
  return [...recommendations].sort((left, right) => {
    if (sortOption === "latest") {
      return compareDates(right.createdAt, left.createdAt);
    }

    const scoreDiff = compareNullableScores(left.fitScore, right.fitScore);
    if (scoreDiff !== 0) {
      return sortOption === "fit_desc" ? -scoreDiff : scoreDiff;
    }

    return compareDates(right.createdAt, left.createdAt);
  });
}

function compareNullableScores(left: number | null, right: number | null) {
  if (left === right) {
    return 0;
  }
  if (left === null) {
    return -1;
  }
  if (right === null) {
    return 1;
  }
  return left - right;
}

function compareDates(left: string, right: string) {
  return new Date(left).getTime() - new Date(right).getTime();
}

function getFallbackReasoning(status: string) {
  if (status === "RULE_REJECTED") {
    return "규칙 기반 필터에서 우선 제외된 공고입니다.";
  }
  return "정밀 평가 대기 중";
}

function buildPlatformOptions(recommendations: DashboardRecommendation[]) {
  const seen = new Set<string>();
  const platforms = ["ALL"];

  for (const recommendation of recommendations) {
    if (seen.has(recommendation.platform)) {
      continue;
    }
    seen.add(recommendation.platform);
    platforms.push(recommendation.platform);
  }

  return platforms;
}

function formatBadgeLabel(value: string) {
  return value
    .toLowerCase()
    .split("_")
    .map((token) => token.charAt(0).toUpperCase() + token.slice(1))
    .join(" ");
}

function formatRelativeDate(value: string) {
  const date = new Date(value);
  return new Intl.DateTimeFormat("ko-KR", {
    month: "numeric",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  }).format(date);
}

function buildSegmentClass(isActive: boolean) {
  return `dashboard-segmented__button${isActive ? " dashboard-segmented__button--active" : ""}`;
}

function buildChipFilterClass(isActive: boolean) {
  return `dashboard-chip-filter${isActive ? " dashboard-chip-filter--active" : ""}`;
}
