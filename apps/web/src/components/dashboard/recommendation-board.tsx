"use client";

import React, { useEffect, useState } from "react";

import type { DashboardRecommendation } from "@/lib/dashboard_mapper";
import { recordEvaluationFeedback } from "@/lib/api_client_browser";
import type { UserProfileResponse } from "@/lib/profile_types";

type RecommendationBoardProps = {
  minimumFitScore: number;
  profile: UserProfileResponse;
  recommendations: DashboardRecommendation[];
};

type SortOption = "latest" | "fit_desc" | "fit_asc";
type FeedbackFilter = "ALL" | "LIKE" | "DISLIKE" | "LATER" | "UNANSWERED";
type SavedView = "recommended" | "review" | "all";
type FeedbackAction = "LIKE" | "DISLIKE" | "LATER";

export function RecommendationBoard({
  minimumFitScore,
  profile,
  recommendations,
}: RecommendationBoardProps) {
  const [recommendationState, setRecommendationState] = useState(recommendations);
  const [onlyQualified, setOnlyQualified] = useState(true);
  const [includeRejected, setIncludeRejected] = useState(false);
  const [sortOption, setSortOption] = useState<SortOption>("latest");
  const [feedbackFilter, setFeedbackFilter] = useState<FeedbackFilter>("ALL");
  const [savedView, setSavedView] = useState<SavedView>("recommended");
  const [platformFilter, setPlatformFilter] = useState("ALL");
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedEvaluationId, setSelectedEvaluationId] = useState<string | null>(null);
  const [selectedFeedbackAction, setSelectedFeedbackAction] = useState<FeedbackAction | null>(null);
  const [feedbackNote, setFeedbackNote] = useState("");
  const [feedbackStatus, setFeedbackStatus] = useState<string | null>(null);
  const [isSavingFeedback, setIsSavingFeedback] = useState(false);

  const platformOptions = buildPlatformOptions(recommendationState);
  const filteredRecommendations = filterRecommendations(recommendationState, {
    minimumFitScore,
    onlyQualified,
    includeRejected,
    feedbackFilter,
    savedView,
    platformFilter,
    searchQuery,
  });
  const sortedRecommendations = sortRecommendations(filteredRecommendations, sortOption);
  const hasSourceRecommendations = recommendationState.length > 0;
  const selectedRecommendation = recommendationState.find(
    (recommendation) => recommendation.evaluationId === selectedEvaluationId,
  );
  const selectedDetail = selectedRecommendation
    ? buildRecommendationDetail(selectedRecommendation, profile, minimumFitScore)
    : null;
  const qualifiesByView = savedView === "all";
  const canIncludeRejected = savedView !== "recommended";

  useEffect(() => {
    if (!selectedEvaluationId) {
      return;
    }

    function handleKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape") {
        setSelectedEvaluationId(null);
      }
    }

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [selectedEvaluationId]);

  async function saveFeedback(
    recommendation: DashboardRecommendation,
    action: FeedbackAction,
    note: string,
  ) {
    setIsSavingFeedback(true);
    setFeedbackStatus(null);

    try {
      const result = await recordEvaluationFeedback(recommendation.evaluationId, {
        feedback: action,
        feedback_reason: note.trim() || null,
      });

      setRecommendationState((current) =>
        current.map((item) =>
          item.evaluationId === recommendation.evaluationId
            ? {
                ...item,
                userFeedback: result.feedback,
                feedbackLabel: formatFeedbackLabel(result.feedback),
                feedbackReason: result.feedback_reason,
              }
            : item,
        ),
      );
      setSelectedFeedbackAction(result.feedback);
      setFeedbackNote(result.feedback_reason ?? note);
      setFeedbackStatus("피드백이 저장되었습니다.");
    } catch (error) {
      setFeedbackStatus(error instanceof Error ? error.message : "피드백 저장에 실패했습니다.");
    } finally {
      setIsSavingFeedback(false);
    }
  }

  async function handleModalFeedbackSave() {
    if (!selectedRecommendation || !selectedFeedbackAction) {
      return;
    }
    await saveFeedback(selectedRecommendation, selectedFeedbackAction, feedbackNote);
  }

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
            {sortedRecommendations.length}개 표시 · 전체 {recommendationState.length}개
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
          <p className="dashboard-meta">
            {savedView === "recommended"
              ? "추천만은 최소 적합도 기준을 자동 적용합니다."
              : savedView === "review"
                ? "검토 필요는 보류, 낮은 점수, 미응답 공고를 우선 보여줍니다."
                : "전체에서만 빠른 조건이 추가로 목록을 좁힙니다."}
          </p>
        </div>

        <div className="dashboard-filter-grid">
          <div className="dashboard-filter-group">
            <span className="dashboard-select__label">빠른 조건</span>
            <div className="dashboard-toggle-list">
              <label className={`dashboard-toggle dashboard-toggle--surface${qualifiesByView ? "" : " dashboard-toggle--disabled"}`}>
                <input
                  checked={qualifiesByView ? onlyQualified : savedView === "recommended"}
                  disabled={!qualifiesByView}
                  onChange={(event) => setOnlyQualified(event.target.checked)}
                  type="checkbox"
                />
                <span>추천 기준 {minimumFitScore}점 이상만 보기</span>
              </label>
              <label className={`dashboard-toggle dashboard-toggle--surface${canIncludeRejected ? "" : " dashboard-toggle--disabled"}`}>
                <input
                  checked={canIncludeRejected ? includeRejected : false}
                  disabled={!canIncludeRejected}
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
                ["LATER", "나중에 보기"],
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
          sortedRecommendations.map((recommendation) => {
            const detail = buildRecommendationDetail(recommendation, profile, minimumFitScore);

            return (
              <article
                className="dashboard-card dashboard-card--interactive dashboard-recommendation"
                key={recommendation.evaluationId}
              >
                <button
                  aria-label={`${recommendation.title} 상세 보기`}
                  className="dashboard-recommendation__button"
                  onClick={() => {
                    setSelectedEvaluationId(recommendation.evaluationId);
                    setSelectedFeedbackAction(
                      recommendation.userFeedback === "LIKE" ||
                        recommendation.userFeedback === "DISLIKE" ||
                        recommendation.userFeedback === "LATER"
                        ? recommendation.userFeedback
                        : null,
                    );
                    setFeedbackNote(recommendation.feedbackReason ?? "");
                    setFeedbackStatus(null);
                  }}
                  type="button"
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
                    {detail.verdict === "추천" ? (
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
                    <span className="dashboard-link dashboard-link--subtle">상세 보기</span>
                  </div>
                </button>
                <div className="dashboard-recommendation__actions">
                  <button
                    className={buildInlineActionClass(recommendation.userFeedback === "LIKE")}
                    disabled={isSavingFeedback}
                    onClick={() => saveFeedback(recommendation, "LIKE", recommendation.feedbackReason ?? "")}
                    type="button"
                  >
                    좋아요
                  </button>
                  <button
                    className={buildInlineActionClass(recommendation.userFeedback === "DISLIKE")}
                    disabled={isSavingFeedback}
                    onClick={() =>
                      saveFeedback(
                        recommendation,
                        "DISLIKE",
                        recommendation.feedbackReason ?? "직접 검토 후 제외",
                      )
                    }
                    type="button"
                  >
                    싫어요
                  </button>
                  <button
                    className={buildInlineActionClass(recommendation.userFeedback === "LATER")}
                    disabled={isSavingFeedback}
                    onClick={() =>
                      saveFeedback(
                        recommendation,
                        "LATER",
                        recommendation.feedbackReason ?? "추가 검토 예정",
                      )
                    }
                    type="button"
                  >
                    나중에 보기
                  </button>
                </div>
              </article>
            );
          })
        )}
      </div>

      {selectedRecommendation && selectedDetail ? (
        <div
          aria-label="공고 상세 패널"
          className="dashboard-detail-overlay"
          onClick={() => setSelectedEvaluationId(null)}
          role="dialog"
        >
          <section
            className="dashboard-card dashboard-detail-modal"
            onClick={(event) => event.stopPropagation()}
          >
            <div className="dashboard-detail-panel__header">
              <div>
                <span className="dashboard-kicker">Detail</span>
                <h2 className="dashboard-section__title">{selectedRecommendation.title}</h2>
                <p className="dashboard-meta">
                  {selectedRecommendation.company} · {selectedRecommendation.platform}
                </p>
              </div>
              <button
                aria-label="상세 패널 닫기"
                className="dashboard-detail-panel__close"
                onClick={() => setSelectedEvaluationId(null)}
                type="button"
              >
                닫기
              </button>
            </div>

            <div className="dashboard-detail-modal__body">
              <section className="dashboard-detail-card dashboard-detail-card--full">
                <div className="dashboard-detail-card__header">
                  <span className="dashboard-kicker">Summary</span>
                  <span className="dashboard-pill">{selectedDetail.verdict}</span>
                </div>
                <div className="dashboard-detail-score">
                  <strong>{selectedRecommendation.fitScore ?? "--"}</strong>
                  <span>{selectedDetail.scoreSummary}</span>
                </div>
                <p className="dashboard-subcopy">{selectedDetail.summary}</p>
              </section>

              <section className="dashboard-detail-card dashboard-detail-card--full">
                <span className="dashboard-kicker">Why Match</span>
                <h3 className="dashboard-recommendation__title">매칭 근거</h3>
                <div className="dashboard-chip-list">
                  {selectedDetail.matchBadges.map((badge) => (
                    <span className="dashboard-chip dashboard-chip--success" key={badge}>
                      {badge}
                    </span>
                  ))}
                </div>
                <ul className="dashboard-detail-list">
                  {selectedDetail.matchReasons.map((reason) => (
                    <li key={reason}>{reason}</li>
                  ))}
                </ul>
              </section>

              <section className="dashboard-detail-card dashboard-detail-card--full">
                <span className="dashboard-kicker">Watchouts</span>
                <h3 className="dashboard-recommendation__title">리스크와 경고</h3>
                <ul className="dashboard-detail-list">
                  {selectedDetail.risks.map((risk) => (
                    <li key={risk}>{risk}</li>
                  ))}
                </ul>
              </section>

              <div className="dashboard-detail-modal__grid">
                <section className="dashboard-detail-card">
                  <span className="dashboard-kicker">Job Snapshot</span>
                  <h3 className="dashboard-recommendation__title">JD 핵심</h3>
                  <div className="dashboard-detail-grid">
                    <div className="dashboard-detail-stat">
                      <span className="dashboard-detail-stat__label">희망 직무와 비교</span>
                      <strong>{profile.profile_data.role}</strong>
                    </div>
                    <div className="dashboard-detail-stat">
                      <span className="dashboard-detail-stat__label">권장 경력 범위</span>
                      <strong>{selectedDetail.experienceRange}</strong>
                    </div>
                    <div className="dashboard-detail-stat">
                      <span className="dashboard-detail-stat__label">근무 조건</span>
                      <strong>{selectedDetail.workMode}</strong>
                    </div>
                    <div className="dashboard-detail-stat">
                      <span className="dashboard-detail-stat__label">위치 힌트</span>
                      <strong>{selectedDetail.location}</strong>
                    </div>
                  </div>
                  <p className="dashboard-detail-copy">{selectedDetail.jobPreview}</p>
                </section>

                <section className="dashboard-detail-card">
                  <span className="dashboard-kicker">My Rules</span>
                  <h3 className="dashboard-recommendation__title">내 기준과 비교</h3>
                  <div className="dashboard-detail-columns">
                    <div>
                      <p className="dashboard-detail-section-title">필수 조건</p>
                      <div className="dashboard-chip-list">
                        {selectedDetail.mustHaveTags.map((tag) => (
                          <span className="dashboard-chip" key={tag}>
                            {tag}
                          </span>
                        ))}
                      </div>
                    </div>
                    <div>
                      <p className="dashboard-detail-section-title">주의 조건</p>
                      <div className="dashboard-chip-list">
                        {selectedDetail.dealBreakerTags.map((tag) => (
                          <span className="dashboard-chip dashboard-chip--warning" key={tag}>
                            {tag}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>
                </section>
              </div>

              <section className="dashboard-detail-card dashboard-detail-card--full">
                <span className="dashboard-kicker">Actions</span>
                <h3 className="dashboard-recommendation__title">피드백 저장</h3>
                <div className="dashboard-segmented dashboard-segmented--actions">
                  {(["LIKE", "DISLIKE", "LATER"] as FeedbackAction[]).map((action) => (
                    <button
                      className={buildModalActionClass(selectedFeedbackAction === action, action)}
                      key={action}
                      onClick={() => setSelectedFeedbackAction(action)}
                      type="button"
                    >
                      {formatFeedbackLabel(action)}
                    </button>
                  ))}
                </div>
                <p className="dashboard-meta">
                  {selectedFeedbackAction
                    ? getFeedbackHelperText(selectedFeedbackAction)
                    : "먼저 피드백 방향을 선택하면 메모 입력 가이드가 바뀝니다."}
                </p>
                <label className="dashboard-search">
                  <span className="dashboard-select__label">피드백 메모</span>
                  <textarea
                    aria-label="피드백 메모"
                    className="dashboard-search__input dashboard-search__input--textarea"
                    onChange={(event) => setFeedbackNote(event.target.value)}
                    placeholder={getFeedbackPlaceholder(selectedFeedbackAction)}
                    value={feedbackNote}
                  />
                </label>
                <button
                  className={buildActionClass(selectedFeedbackAction)}
                  disabled={isSavingFeedback || selectedFeedbackAction === null}
                  onClick={handleModalFeedbackSave}
                  type="button"
                >
                  {selectedFeedbackAction
                    ? `${formatFeedbackLabel(selectedFeedbackAction)} 저장`
                    : "피드백 선택 후 저장"}
                </button>
                {feedbackStatus ? <p className="dashboard-meta">{feedbackStatus}</p> : null}
              </section>
            </div>

            <div className="dashboard-detail-panel__footer">
              <a
                className="dashboard-link"
                href={selectedRecommendation.url}
                rel="noreferrer"
                target="_blank"
              >
                원문 공고 보기
              </a>
            </div>
          </section>
        </div>
      ) : null}
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
      !isRejected &&
      (recommendation.status === "PENDING" ||
        recommendation.userFeedback === null ||
        (recommendation.fitScore !== null && recommendation.fitScore < filters.minimumFitScore));

    if (filters.savedView === "recommended" && !isQualified) {
      return false;
    }

    if (filters.savedView === "review") {
      if (!needsReview && !(filters.includeRejected && isRejected)) {
        return false;
      }
    }

    if (filters.savedView === "all") {
      if (!filters.includeRejected && isRejected) {
        return false;
      }
      if (filters.onlyQualified && !isQualified) {
        return false;
      }
    } else if (!filters.includeRejected && isRejected) {
      return false;
    }

    if (filters.feedbackFilter === "LIKE" && recommendation.userFeedback !== "LIKE") {
      return false;
    }
    if (filters.feedbackFilter === "DISLIKE" && recommendation.userFeedback !== "DISLIKE") {
      return false;
    }
    if (filters.feedbackFilter === "LATER" && recommendation.userFeedback !== "LATER") {
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

    const searchableText = `${recommendation.title} ${recommendation.company} ${recommendation.jdRawText}`.toLowerCase();
    return searchableText.includes(normalizedQuery);
  });
}

function sortRecommendations(recommendations: DashboardRecommendation[], sortOption: SortOption) {
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

function buildRecommendationDetail(
  recommendation: DashboardRecommendation,
  profile: UserProfileResponse,
  minimumFitScore: number,
) {
  const normalizedText = `${recommendation.title} ${recommendation.jdRawText} ${JSON.stringify(recommendation.sourceMetadata)}`.toLowerCase();
  const mustHaves = profile.guidelines.must_haves;
  const dealBreakers = profile.guidelines.deal_breakers;
  const matchedMustHaves = mustHaves.filter((item) => normalizedText.includes(item.toLowerCase()));
  const flaggedDealBreakers = dealBreakers.filter((item) => normalizedText.includes(item.toLowerCase()));
  const verdict = getVerdict(recommendation, minimumFitScore);
  const matchReasons: string[] = [];
  const risks: string[] = [];
  const backendMatchHighlights = recommendation.matchHighlights;
  const backendRiskHighlights = recommendation.riskHighlights;
  const backendRuleMatchReasons = recommendation.ruleMatchReasons;
  const backendRuleRejectionDetails = recommendation.ruleRejectionDetails;

  if (recommendation.fitScore !== null) {
    matchReasons.push(`현재 적합도는 ${recommendation.fitScore}점으로 최소 기준 ${minimumFitScore}점과 비교됩니다.`);
  }

  if (matchedMustHaves.length > 0) {
    matchReasons.push(`필수 조건 중 ${matchedMustHaves.join(", ")} 항목이 공고 설명에서 직접 확인됩니다.`);
  } else {
    risks.push("필수 조건과 직접적으로 매칭되는 키워드가 적어 설명을 더 확인할 필요가 있습니다.");
  }

  if (recommendation.minYearsExperience !== null || recommendation.maxYearsExperience !== null) {
    const years = profile.profile_data.years_of_experience;
    const lowerBound = recommendation.minYearsExperience ?? 0;
    const upperBound = recommendation.maxYearsExperience ?? 99;
    if (years >= lowerBound && years <= upperBound) {
      matchReasons.push(`내 경력 ${years}년이 권장 범위 ${formatExperienceRange(recommendation)} 안에 들어옵니다.`);
    } else {
      risks.push(`내 경력 ${years}년과 공고의 권장 범위 ${formatExperienceRange(recommendation)}가 어긋날 수 있습니다.`);
    }
  } else {
    risks.push("공고에 경력 범위가 명확하게 적혀 있지 않아 직급 적합도를 사람이 한 번 더 판단해야 합니다.");
  }

  if (flaggedDealBreakers.length > 0) {
    risks.push(`주의 조건 ${flaggedDealBreakers.join(", ")} 가 공고 설명이나 메타데이터에서 감지됩니다.`);
  }

  if (recommendation.ruleRejectionReason) {
    risks.push(`규칙 기반 필터 제외 사유는 ${formatBadgeLabel(recommendation.ruleRejectionReason)} 입니다.`);
  }

  if (recommendation.userFeedback && recommendation.feedbackLabel) {
    matchReasons.push(`현재 저장된 피드백 상태는 ${recommendation.feedbackLabel} 입니다.`);
  }

  if (recommendation.userFeedback === "DISLIKE" && recommendation.feedbackReason) {
    risks.push(`과거 피드백 메모: ${recommendation.feedbackReason}`);
  }

  if (risks.length === 0) {
    risks.push("즉시 보이는 리스크는 적지만, JD 원문에서 실제 책임 범위와 팀 맥락은 확인하는 것이 좋습니다.");
  }

  return {
    verdict,
    scoreSummary:
      recommendation.fitScore === null
        ? "정밀 평가 전 단계"
        : recommendation.fitScore >= minimumFitScore
          ? `기준 대비 +${recommendation.fitScore - minimumFitScore}`
          : `기준 대비 ${recommendation.fitScore - minimumFitScore}`,
    summary:
      recommendation.decisionSummary ??
      recommendation.reasoning ??
      (verdict === "보류"
        ? "아직 정밀 평가가 끝나지 않았거나 추가 확인이 필요한 공고입니다."
        : verdict === "비추천"
          ? "규칙 필터나 낮은 적합도로 인해 우선순위가 낮은 공고입니다."
          : "프로필 기준에서 주요 조건이 맞아 떨어지는 공고입니다."),
    matchBadges:
      backendMatchHighlights.length > 0
        ? backendMatchHighlights.slice(0, 4)
        : matchedMustHaves.length > 0
          ? matchedMustHaves.slice(0, 4)
          : ["직무 맥락 확인 필요"],
    matchReasons: backendRuleMatchReasons.length > 0 ? backendRuleMatchReasons : matchReasons,
    risks:
      backendRiskHighlights.length > 0 || backendRuleRejectionDetails.length > 0
        ? [...backendRiskHighlights, ...backendRuleRejectionDetails]
        : risks,
    experienceRange: formatExperienceRange(recommendation),
    workMode:
      recommendation.employmentType ??
      readMetadataLabel(recommendation.sourceMetadata, [
        "employment_type",
        "experience_text",
        "employmentType",
      ]),
    location:
      recommendation.location ??
      readMetadataLabel(recommendation.sourceMetadata, ["location", "region", "workplace"]),
    jobPreview:
      recommendation.responsibilities.length > 0
        ? recommendation.responsibilities.join(" · ")
        : truncateText(recommendation.jdRawText, 320),
    mustHaveTags: mustHaves.length > 0 ? mustHaves : ["아직 필수 조건 없음"],
    dealBreakerTags: dealBreakers.length > 0 ? dealBreakers : ["아직 비선호 조건 없음"],
  };
}

function getVerdict(recommendation: DashboardRecommendation, minimumFitScore: number) {
  if (recommendation.status === "RULE_REJECTED") {
    return "비추천";
  }
  if (recommendation.status === "PENDING") {
    return "보류";
  }
  if (recommendation.fitScore !== null && recommendation.fitScore >= minimumFitScore) {
    return "추천";
  }
  return "보류";
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

function formatExperienceRange(recommendation: DashboardRecommendation) {
  if (recommendation.minYearsExperience === null && recommendation.maxYearsExperience === null) {
    return "명시 없음";
  }
  if (recommendation.minYearsExperience !== null && recommendation.maxYearsExperience !== null) {
    return `${recommendation.minYearsExperience}년 ~ ${recommendation.maxYearsExperience}년`;
  }
  if (recommendation.minYearsExperience !== null) {
    return `${recommendation.minYearsExperience}년 이상`;
  }
  return `${recommendation.maxYearsExperience}년 이하`;
}

function readMetadataLabel(sourceMetadata: Record<string, unknown>, keys: string[]) {
  for (const key of keys) {
    const value = sourceMetadata[key];
    if (typeof value === "string" && value.trim().length > 0) {
      return value;
    }
  }
  return "정보 없음";
}

function truncateText(value: string, maxLength: number) {
  const normalized = value.trim();
  if (normalized.length <= maxLength) {
    return normalized;
  }
  return `${normalized.slice(0, maxLength).trimEnd()}...`;
}

function buildSegmentClass(isActive: boolean) {
  return `dashboard-segmented__button${isActive ? " dashboard-segmented__button--active" : ""}`;
}

function buildChipFilterClass(isActive: boolean) {
  return `dashboard-chip-filter${isActive ? " dashboard-chip-filter--active" : ""}`;
}

function buildActionClass(action: FeedbackAction | null) {
  const suffix = action ? action.toLowerCase() : "neutral";
  return `dashboard-action-button dashboard-action-button--${suffix}`;
}

function formatFeedbackLabel(feedback: FeedbackAction) {
  if (feedback === "LIKE") {
    return "좋아요";
  }
  if (feedback === "DISLIKE") {
    return "제외";
  }
  return "나중에 보기";
}

function buildInlineActionClass(isActive: boolean) {
  return `dashboard-inline-action${isActive ? " dashboard-inline-action--active" : ""}`;
}

function buildModalActionClass(isActive: boolean, action: FeedbackAction) {
  return `dashboard-segmented__button dashboard-segmented__button--${action.toLowerCase()}${isActive ? " dashboard-segmented__button--active" : ""}`;
}

function getFeedbackPlaceholder(action: FeedbackAction | null) {
  if (action === "LIKE") {
    return "어떤 점이 특히 잘 맞는지 남겨보세요";
  }
  if (action === "DISLIKE") {
    return "왜 제외하려는지 간단히 남겨보세요";
  }
  if (action === "LATER") {
    return "다시 볼 시점이나 확인할 포인트를 남겨보세요";
  }
  return "먼저 피드백 방향을 선택해 주세요";
}

function getFeedbackHelperText(action: FeedbackAction) {
  if (action === "LIKE") {
    return "좋아요는 이후 비슷한 공고를 더 자주 추천하는 데 도움이 됩니다.";
  }
  if (action === "DISLIKE") {
    return "싫어요는 단기 메모리에 반영되어 비슷한 공고를 줄이는 데 사용됩니다.";
  }
  return "나중에 보기는 관심은 있지만 아직 판단 전인 공고를 분리해두는 용도입니다.";
}
