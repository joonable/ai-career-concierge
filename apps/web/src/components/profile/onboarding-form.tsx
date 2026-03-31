"use client";

import React, { startTransition, useMemo, useState } from "react";

import { updateProfile } from "@/lib/api_client_browser";
import type { Preferences, UserProfilePayload, UserProfileResponse } from "@/lib/profile_types";

type OnboardingFormProps = {
  initialProfile: UserProfileResponse;
};

type ToneOption = {
  id: string;
  label: string;
  meta?: string;
};

type ComparisonPrompt = {
  id: string;
  leftLabel: string;
  rightLabel: string;
  description: string;
};

type StatusTone = "neutral" | "success" | "error";

type PreferenceState = {
  selectedRoles: string[];
  selectedSeniority: string[];
  selectedWorkModes: string[];
  selectedLocations: string[];
  selectedTeamContexts: string[];
  selectedSkills: string[];
  customSkills: string[];
  selectedExclusions: string[];
  customExclusions: string[];
  comparisonState: Record<string, number | null>;
  note: string;
  minimumFitScore: string;
};

const roleOptions: ToneOption[] = [
  { id: "ml-engineer", label: "ML Engineer" },
  { id: "llm-engineer", label: "LLM Engineer" },
  { id: "data-scientist", label: "Data Scientist" },
  { id: "mlops", label: "MLOps Engineer" },
  { id: "backend-ai", label: "Backend Engineer (AI/Data)" },
];

const seniorityOptions: ToneOption[] = [
  { id: "junior", label: "주니어", meta: "0-2년" },
  { id: "mid", label: "미드", meta: "3-5년" },
  { id: "senior", label: "시니어", meta: "6-9년" },
  { id: "staff", label: "스태프+", meta: "10년 이상" },
];

const workModeOptions: ToneOption[] = [
  { id: "remote", label: "원격" },
  { id: "hybrid", label: "하이브리드" },
  { id: "onsite", label: "상주 출근" },
];

const locationOptions: ToneOption[] = [
  { id: "seoul", label: "서울" },
  { id: "pangyo", label: "판교" },
  { id: "bundang", label: "분당" },
  { id: "gyeonggi", label: "경기권" },
  { id: "daejeon", label: "대전" },
  { id: "busan", label: "부산" },
  { id: "nationwide", label: "전국 어디든" },
  { id: "global", label: "해외 포함" },
];

const teamContextOptions: ToneOption[] = [
  { id: "ai-first", label: "AI/ML 팀이 핵심 조직", meta: "회사 안에서 ML 직무의 존재감이 큰 편" },
  { id: "product-team", label: "프로덕트와 가까운 역할", meta: "모델을 실제 제품 지표와 연결" },
  { id: "platform-team", label: "플랫폼/인프라와 맞닿은 역할", meta: "서빙, 파이프라인, 운영도 함께 다룸" },
  { id: "small-team", label: "작은 팀에서 폭넓게 담당", meta: "역할 범위가 넓고 자율성이 큼" },
  { id: "specialist-team", label: "전문성 높은 팀 분업", meta: "역할 경계가 비교적 또렷함" },
];

const skillOptions: ToneOption[] = [
  { id: "python", label: "Python" },
  { id: "sql", label: "SQL" },
  { id: "pytorch", label: "PyTorch" },
  { id: "tensorflow", label: "TensorFlow" },
  { id: "llm", label: "LLM application" },
  { id: "rag", label: "RAG" },
  { id: "evaluation", label: "LLM evaluation" },
  { id: "airflow", label: "Airflow / orchestration" },
  { id: "mlops", label: "MLOps / serving" },
  { id: "aws", label: "AWS / cloud" },
  { id: "backend", label: "Backend API" },
  { id: "analytics", label: "Experimentation / analytics" },
];

const exclusionOptions: ToneOption[] = [
  { id: "contract", label: "계약직 중심" },
  { id: "internship", label: "인턴 포지션" },
  { id: "onsite-only", label: "상주 출근만 가능" },
  { id: "research-heavy", label: "리서치 성향이 너무 강함" },
  { id: "no-llm", label: "LLM 업무가 전혀 없음" },
  { id: "korean-required", label: "한국어 필수" },
  { id: "visa-none", label: "비자 지원 없음" },
];

const comparisonPrompts: ComparisonPrompt[] = [
  {
    id: "delivery-vs-research",
    leftLabel: "모델 개발 중심",
    rightLabel: "서비스 적용 중심",
    description: "업무 무게중심이 어디에 가까우면 좋은지 빠르게 맞춥니다.",
  },
  {
    id: "company-shape",
    leftLabel: "작은 팀 자율성",
    rightLabel: "큰 조직 안정성",
    description: "팀 구조와 의사결정 방식의 선호를 가볍게 반영합니다.",
  },
  {
    id: "llm-vs-classic",
    leftLabel: "LLM 응용 중심",
    rightLabel: "전통 ML 중심",
    description: "요즘 보고 싶은 문제 유형이 어디에 더 가까운지 확인합니다.",
  },
  {
    id: "ownership-shape",
    leftLabel: "한 문제를 깊게 파는 역할",
    rightLabel: "여러 영역을 넓게 맡는 역할",
    description: "전문성의 깊이와 역할 범위 중 어디에 더 끌리는지 확인합니다.",
  },
  {
    id: "speed-vs-process",
    leftLabel: "빠른 실행과 실험",
    rightLabel: "정교한 프로세스와 안정성",
    description: "업무 템포와 의사결정 방식의 선호를 추가로 읽어냅니다.",
  },
  {
    id: "build-vs-operate",
    leftLabel: "새 시스템 구축 비중",
    rightLabel: "운영 최적화 비중",
    description: "0→1에 가까운 일과 운영 개선 일의 선호를 구분합니다.",
  },
];

const comparisonScale = [-2, -1, 0, 1, 2] as const;

const scaleValueToLabel = new Map<number, string>([
  [-2, "강하게 왼쪽"],
  [-1, "약하게 왼쪽"],
  [0, "중립"],
  [1, "약하게 오른쪽"],
  [2, "강하게 오른쪽"],
]);

function normalizeKeyword(value: string) {
  return value.trim().replace(/\s+/g, " ");
}

function matchListOptions(values: string[], options: ToneOption[]) {
  const byLabel = new Map(
    options.flatMap((option) => [
      [option.label.toLowerCase(), option.id],
      [option.id.toLowerCase(), option.id],
    ]),
  );
  const selected = new Set<string>();
  const remaining: string[] = [];

  values.forEach((value) => {
    const optionId = byLabel.get(value.toLowerCase());
    if (optionId) {
      selected.add(optionId);
    } else {
      remaining.push(value);
    }
  });

  return {
    selected: [...selected],
    remaining,
  };
}

function yearsToSeniority(yearsOfExperience: string) {
  const years = Number(yearsOfExperience);
  if (!Number.isFinite(years) || years <= 0) {
    return [];
  }
  if (years <= 2) {
    return ["junior"];
  }
  if (years <= 5) {
    return ["mid"];
  }
  if (years <= 9) {
    return ["senior"];
  }
  return ["staff"];
}

function seniorityToYears(selectedSeniority: string[], fallbackYearsOfExperience: string) {
  if (selectedSeniority.includes("staff")) {
    return 10;
  }
  if (selectedSeniority.includes("senior")) {
    return 7;
  }
  if (selectedSeniority.includes("mid")) {
    return 4;
  }
  if (selectedSeniority.includes("junior")) {
    return 1;
  }
  return Number(fallbackYearsOfExperience) || 0;
}

function buildTitleKeywords(selectedRoleIds: string[], selectedRoleLabels: string[]) {
  const roleKeywords = selectedRoleIds.map((roleId) => roleId.replace(/-/g, " "));
  return dedupe([...selectedRoleLabels.map((label) => label.toLowerCase()), ...roleKeywords]);
}

function hasStructuredPreferences(preferences: Preferences) {
  return Boolean(
    preferences.work_modes.length > 0 ||
      preferences.locations.length > 0 ||
      preferences.team_contexts.length > 0 ||
      preferences.skills.preset.length > 0 ||
      preferences.skills.custom.length > 0 ||
      preferences.exclusions.preset.length > 0 ||
      preferences.exclusions.custom.length > 0 ||
      Object.keys(preferences.comparisons).length > 0 ||
      preferences.note,
  );
}

function dedupe(values: string[]) {
  const seen = new Set<string>();
  return values.filter((value) => {
    const normalized = value.toLowerCase();
    if (seen.has(normalized)) {
      return false;
    }
    seen.add(normalized);
    return true;
  });
}

function buildInitialPreferenceState(initialProfile: UserProfileResponse): PreferenceState {
  const preferences = initialProfile.preferences;
  const shouldUseStructured = hasStructuredPreferences(preferences);
  const storedRoles = initialProfile.profile_data.roles ?? [];
  const storedPrimaryRole = initialProfile.profile_data.primary_role ?? "";
  const storedRole = initialProfile.profile_data.role;
  const storedSeniority = initialProfile.profile_data.seniority ?? "";

  const skillSource = shouldUseStructured
    ? [...preferences.skills.preset, ...preferences.skills.custom]
    : initialProfile.guidelines.must_haves;
  const exclusionSource = shouldUseStructured
    ? [...preferences.exclusions.preset, ...preferences.exclusions.custom]
    : initialProfile.guidelines.deal_breakers;

  const matchedSkills = matchListOptions(skillSource, skillOptions);
  const matchedExclusions = matchListOptions(exclusionSource, exclusionOptions);

  return {
    selectedRoles:
      storedRoles.length > 0
        ? matchListOptions(storedRoles, roleOptions).selected
        : matchListOptions([storedPrimaryRole || storedRole].filter(Boolean), roleOptions).selected,
    selectedSeniority:
      storedSeniority.trim().length > 0
        ? [storedSeniority]
        : yearsToSeniority(String(initialProfile.profile_data.years_of_experience)),
    selectedWorkModes: preferences.work_modes,
    selectedLocations: preferences.locations,
    selectedTeamContexts: preferences.team_contexts,
    selectedSkills: matchedSkills.selected,
    customSkills: matchedSkills.remaining,
    selectedExclusions: matchedExclusions.selected,
    customExclusions: matchedExclusions.remaining,
    comparisonState: Object.fromEntries(
      comparisonPrompts.map((prompt) => [prompt.id, preferences.comparisons[prompt.id] ?? null]),
    ),
    note: preferences.note ?? "",
    minimumFitScore: String(initialProfile.notification_settings.minimum_fit_score),
  };
}

function buildPayload(state: PreferenceState): UserProfilePayload {
  const selectedRoleOptions = roleOptions.filter((option) => state.selectedRoles.includes(option.id));
  const selectedRoleLabels = selectedRoleOptions.map((option) => option.label);
  const selectedComparisonEntries = comparisonPrompts
    .filter((prompt) => state.comparisonState[prompt.id] !== null)
    .map((prompt) => [prompt.id, state.comparisonState[prompt.id] ?? 0] as const);
  const yearsOfExperience = seniorityToYears(
    state.selectedSeniority,
    "0",
  );
  const primaryRoleId = state.selectedRoles[0] ?? "";
  const primaryRoleLabel = selectedRoleLabels[0] ?? "";

  return {
    profile_data: {
      role: primaryRoleLabel,
      roles: state.selectedRoles,
      primary_role: primaryRoleId,
      years_of_experience: yearsOfExperience,
      seniority: state.selectedSeniority[0] ?? "",
      title_keywords: buildTitleKeywords(state.selectedRoles, selectedRoleLabels),
    },
    preferences: {
      work_modes: state.selectedWorkModes,
      locations: state.selectedLocations,
      team_contexts: state.selectedTeamContexts,
      skills: {
        preset: state.selectedSkills,
        custom: dedupe(state.customSkills),
      },
      exclusions: {
        preset: state.selectedExclusions,
        custom: dedupe(state.customExclusions),
      },
      comparisons: Object.fromEntries(selectedComparisonEntries),
      note: state.note.trim().length > 0 ? state.note.trim() : null,
    },
    notification_settings: {
      minimum_fit_score: Number(state.minimumFitScore) || 80,
    },
  };
}

function ToggleGroup({
  label,
  options,
  selected,
  onToggle,
  helper = "클릭해서 여러 개를 바로 조합할 수 있습니다.",
}: {
  label: string;
  options: ToneOption[];
  selected: string[];
  onToggle: (id: string) => void;
  helper?: string;
}) {
  return (
    <section className="onboarding-mockup__block">
      <div className="onboarding-mockup__block-header">
        <div>
          <span className="dashboard-detail__label">{label}</span>
          <p className="onboarding-mockup__helper">{helper}</p>
        </div>
      </div>
      <div className="onboarding-choice-grid" role="list" aria-label={label}>
        {options.map((option) => {
          const isSelected = selected.includes(option.id);
          return (
            <button
              aria-pressed={isSelected}
              className={[
                "onboarding-choice-chip",
                isSelected ? "onboarding-choice-chip--selected" : "",
              ].join(" ")}
              key={option.id}
              onClick={() => onToggle(option.id)}
              type="button"
            >
              <span>{option.label}</span>
              {option.meta ? <small>{option.meta}</small> : null}
            </button>
          );
        })}
      </div>
    </section>
  );
}

export function OnboardingForm({ initialProfile }: OnboardingFormProps) {
  const [state, setState] = useState(() => buildInitialPreferenceState(initialProfile));
  const [skillInput, setSkillInput] = useState("");
  const [exclusionInput, setExclusionInput] = useState("");
  const [isPending, setIsPending] = useState(false);
  const [status, setStatus] = useState({
    tone: "neutral" as StatusTone,
    message: "설정을 저장하면 다음 추천부터 바로 반영됩니다.",
  });

  const completedSections = [
    state.selectedRoles.length > 0,
    state.selectedSeniority.length > 0,
    state.selectedWorkModes.length > 0 || state.selectedLocations.length > 0,
    state.selectedSkills.length + state.customSkills.length > 0,
    state.selectedExclusions.length + state.customExclusions.length > 0,
  ].filter(Boolean).length;

  const summaryItems = useMemo(
    () => [
      {
        label: "직무",
        value:
          state.selectedRoles.length > 0
            ? roleOptions
                .filter((option) => state.selectedRoles.includes(option.id))
                .map((option) => option.label)
                .join(", ")
            : "None",
      },
      {
        label: "경력",
        value:
          state.selectedSeniority.length > 0
            ? seniorityOptions
                .filter((option) => state.selectedSeniority.includes(option.id))
                .map((option) => option.label)
                .join(", ")
            : "None",
      },
      {
        label: "근무/지역",
        value: `${state.selectedWorkModes.length} / ${state.selectedLocations.length}`,
      },
      { label: "스킬", value: `${state.selectedSkills.length + state.customSkills.length}개` },
      {
        label: "제외 조건",
        value: `${state.selectedExclusions.length + state.customExclusions.length}개`,
      },
      { label: "보조 메모", value: state.note.trim().length > 0 ? "입력됨" : "None" },
    ],
    [state],
  );

  const selectedComparisons = comparisonPrompts.filter(
    (prompt) => state.comparisonState[prompt.id] !== null,
  );

  const toggleSelection = (
    id: string,
    key:
      | "selectedRoles"
      | "selectedSeniority"
      | "selectedWorkModes"
      | "selectedLocations"
      | "selectedTeamContexts"
      | "selectedSkills"
      | "selectedExclusions",
  ) => {
    setState((current) => ({
      ...current,
      [key]: current[key].includes(id)
        ? current[key].filter((item) => item !== id)
        : [...current[key], id],
    }));
  };

  const addKeyword = (
    rawValue: string,
    key: "customSkills" | "customExclusions",
    clear: () => void,
  ) => {
    const normalized = normalizeKeyword(rawValue);
    if (!normalized) {
      return;
    }

    setState((current) => ({
      ...current,
      [key]: current[key].some((item) => item.toLowerCase() === normalized.toLowerCase())
        ? current[key]
        : [...current[key], normalized],
    }));
    clear();
  };

  const removeKeyword = (keyword: string, key: "customSkills" | "customExclusions") => {
    setState((current) => ({
      ...current,
      [key]: current[key].filter((item) => item !== keyword),
    }));
  };

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setIsPending(true);
    setStatus({
      tone: "neutral",
      message: "설정을 저장하고 있습니다.",
    });

    startTransition(async () => {
      try {
        await updateProfile(buildPayload(state));
        setStatus({
          tone: "success",
          message: "추천 기준을 저장했습니다. 대시보드로 이동합니다.",
        });
        window.location.href = "/dashboard";
      } catch (error) {
        setStatus({
          tone: "error",
          message: `저장 실패: ${error instanceof Error ? error.message : "프로필을 저장하지 못했습니다."}`,
        });
      } finally {
        setIsPending(false);
      }
    });
  };

  return (
    <section className="dashboard-card onboarding-form-card onboarding-mockup">
      <div className="onboarding-form__header">
        <div className="dashboard-summary-card__copy">
          <span className="dashboard-kicker">추천 기준</span>
          <h2 className="dashboard-section__title">어떤 공고를 받고 싶은지 알려주세요</h2>
        </div>
        <span className="dashboard-pill">실시간 요약</span>
      </div>

      <div className="onboarding-summary-grid" role="list">
        {summaryItems.map((item) => (
          <div className="onboarding-summary-item" key={item.label} role="listitem">
            <span className="onboarding-summary-item__label">{item.label}</span>
            <div className="onboarding-summary-item__value-row">
              <span className="onboarding-summary-item__value">{item.value}</span>
            </div>
          </div>
        ))}
      </div>

      <form className="onboarding-form" onSubmit={handleSubmit}>
        <div className="onboarding-mockup__layout">
          <div className="onboarding-mockup__main">
            <ToggleGroup
              label="보고 싶은 직무"
              onToggle={(id) => toggleSelection(id, "selectedRoles")}
              options={roleOptions}
              selected={state.selectedRoles}
            />
            <ToggleGroup
              label="경력 레벨"
              onToggle={(id) => toggleSelection(id, "selectedSeniority")}
              options={seniorityOptions}
              selected={state.selectedSeniority}
              helper="연차 힌트를 함께 보여드려서 현재 보고 싶은 수준을 빠르게 고를 수 있어요."
            />
            <ToggleGroup
              label="근무 형태"
              onToggle={(id) => toggleSelection(id, "selectedWorkModes")}
              options={workModeOptions}
              selected={state.selectedWorkModes}
              helper="출근 조건은 추천 결과를 빠르게 좁히는 데 가장 먼저 쓰입니다."
            />
            <ToggleGroup
              label="지역"
              onToggle={(id) => toggleSelection(id, "selectedLocations")}
              options={locationOptions}
              selected={state.selectedLocations}
              helper="실제로 탐색할 범위를 바로 이해할 수 있게 지역을 넓게 준비했습니다."
            />
            <ToggleGroup
              label="일하고 싶은 팀 맥락"
              onToggle={(id) => toggleSelection(id, "selectedTeamContexts")}
              options={teamContextOptions}
              selected={state.selectedTeamContexts}
              helper="회사 단계 대신, 실제 공고에서 느껴지는 팀 분위기와 역할 구조를 고릅니다."
            />

            <section className="onboarding-mockup__block">
              <div className="onboarding-mockup__block-header">
                <div>
                  <span className="dashboard-detail__label">빠르게 제외할 조건</span>
                  <p className="onboarding-mockup__helper">
                    공고에서 비교적 명확하게 읽히는 조건만 담았습니다.
                  </p>
                </div>
              </div>
              <div className="onboarding-choice-grid" role="list" aria-label="빠르게 제외할 조건">
                {exclusionOptions.map((option) => {
                  const isSelected = state.selectedExclusions.includes(option.id);
                  return (
                    <button
                      aria-pressed={isSelected}
                      className={[
                        "onboarding-choice-chip",
                        "onboarding-choice-chip--danger",
                        isSelected ? "onboarding-choice-chip--selected" : "",
                      ].join(" ")}
                      key={option.id}
                      onClick={() => toggleSelection(option.id, "selectedExclusions")}
                      type="button"
                    >
                      <span>{option.label}</span>
                    </button>
                  );
                })}
              </div>
              <div className="onboarding-keyword-input">
                <input
                  className="onboarding-field__input"
                  name="customExclusion"
                  onChange={(event) => setExclusionInput(event.target.value)}
                  onKeyDown={(event) => {
                    if (event.key === "Enter") {
                      event.preventDefault();
                      addKeyword(exclusionInput, "customExclusions", () => setExclusionInput(""));
                    }
                  }}
                  placeholder="직접 제외 키워드 추가, 예: 박사 학위 필수"
                  value={exclusionInput}
                />
                <button
                  className="onboarding-inline-button"
                  onClick={() => addKeyword(exclusionInput, "customExclusions", () => setExclusionInput(""))}
                  type="button"
                >
                  추가
                </button>
              </div>
              <div className="onboarding-choice-grid" role="list" aria-label="직접 입력한 제외 키워드">
                {state.customExclusions.map((keyword) => (
                  <button
                    className="onboarding-choice-chip onboarding-choice-chip--selected onboarding-choice-chip--danger"
                    key={keyword}
                    onClick={() => removeKeyword(keyword, "customExclusions")}
                    type="button"
                  >
                    <span>{keyword}</span>
                    <small>클릭해서 제거</small>
                  </button>
                ))}
              </div>
            </section>

            <section className="onboarding-mockup__block">
              <div className="onboarding-mockup__block-header">
                <div>
                  <span className="dashboard-detail__label">중요하게 볼 스킬</span>
                  <p className="onboarding-mockup__helper">
                    추천 정확도에 영향을 크게 주는 항목이라, 빠른 선택과 직접 입력을 함께 지원합니다.
                  </p>
                </div>
              </div>
              <div className="onboarding-choice-grid" role="list" aria-label="중요하게 볼 스킬">
                {skillOptions.map((option) => {
                  const isSelected = state.selectedSkills.includes(option.id);
                  return (
                    <button
                      aria-pressed={isSelected}
                      className={[
                        "onboarding-choice-chip",
                        isSelected ? "onboarding-choice-chip--selected" : "",
                      ].join(" ")}
                      key={option.id}
                      onClick={() => toggleSelection(option.id, "selectedSkills")}
                      type="button"
                    >
                      <span>{option.label}</span>
                    </button>
                  );
                })}
              </div>
              <div className="onboarding-keyword-input">
                <input
                  className="onboarding-field__input"
                  name="customSkill"
                  onChange={(event) => setSkillInput(event.target.value)}
                  onKeyDown={(event) => {
                    if (event.key === "Enter") {
                      event.preventDefault();
                      addKeyword(skillInput, "customSkills", () => setSkillInput(""));
                    }
                  }}
                  placeholder="직접 스킬 키워드 추가, 예: Spark, 추천 시스템, LangChain"
                  value={skillInput}
                />
                <button
                  className="onboarding-inline-button"
                  onClick={() => addKeyword(skillInput, "customSkills", () => setSkillInput(""))}
                  type="button"
                >
                  추가
                </button>
              </div>
              <div className="onboarding-choice-grid" role="list" aria-label="직접 입력한 스킬">
                {state.customSkills.map((keyword) => (
                  <button
                    className="onboarding-choice-chip onboarding-choice-chip--selected"
                    key={keyword}
                    onClick={() => removeKeyword(keyword, "customSkills")}
                    type="button"
                  >
                    <span>{keyword}</span>
                    <small>클릭해서 제거</small>
                  </button>
                ))}
              </div>
            </section>

            <details
              className="onboarding-advanced"
              onToggle={(event) =>
                setState((current) => ({
                  ...current,
                  comparisonState: current.comparisonState,
                }))
              }
            >
              <summary className="onboarding-advanced__summary">
                <div>
                  <span className="dashboard-detail__label">고급 설정</span>
                  <p className="onboarding-mockup__helper">기본 선택만으로 충분하다면 건너뛰어도 됩니다.</p>
                </div>
                <span className="dashboard-pill">펼치기</span>
              </summary>
              <div className="onboarding-advanced__content">
                <div className="onboarding-comparison-list">
                  {comparisonPrompts.map((prompt) => (
                    <article className="onboarding-comparison-card" key={prompt.id}>
                      <div className="onboarding-comparison-scale" role="group" aria-label={prompt.description}>
                        <div className="onboarding-slider">
                          <div className="onboarding-slider__labels" aria-hidden="true">
                            <span>{prompt.leftLabel}</span>
                            <span>{prompt.rightLabel}</span>
                          </div>
                          <input
                            aria-label={`${prompt.leftLabel}와 ${prompt.rightLabel} 사이 선호도`}
                            className="onboarding-slider__input"
                            max={2}
                            min={-2}
                            onChange={(event) =>
                              setState((current) => ({
                                ...current,
                                comparisonState: {
                                  ...current.comparisonState,
                                  [prompt.id]: Number(event.target.value),
                                },
                              }))
                            }
                            step={1}
                            type="range"
                            value={state.comparisonState[prompt.id] ?? 0}
                          />
                          <div className="onboarding-slider__dots" aria-hidden="true">
                            {comparisonScale.map((value) => (
                              <span
                                className={[
                                  "onboarding-slider__dot",
                                  state.comparisonState[prompt.id] === value
                                    ? "onboarding-slider__dot--selected"
                                    : "",
                                ].join(" ")}
                                key={value}
                              />
                            ))}
                          </div>
                        </div>
                      </div>
                    </article>
                  ))}
                </div>
              </div>
            </details>

            <section className="onboarding-mockup__block">
              <div className="onboarding-mockup__block-header">
                <div>
                  <span className="dashboard-detail__label">보조 메모</span>
                  <p className="onboarding-mockup__helper">
                    선택만으로 담기 어려운 내용이 있다면 짧게 남겨주세요.
                  </p>
                </div>
              </div>
              <textarea
                className="onboarding-field__input onboarding-field__textarea"
                name="mockupNote"
                onChange={(event) => setState((current) => ({ ...current, note: event.target.value }))}
                placeholder="필요한 경우에만 짧게 남겨주세요"
                value={state.note}
              />
            </section>

            <section className="onboarding-mockup__block">
              <div className="onboarding-form__grid">
                <label className="onboarding-field onboarding-field--wide">
                  <span>최소 적합도 점수</span>
                  <input
                    className="onboarding-field__input"
                    inputMode="numeric"
                    max={100}
                    min={0}
                    name="minimumFitScore"
                    onChange={(event) =>
                      setState((current) => ({ ...current, minimumFitScore: event.target.value }))
                    }
                    placeholder="80"
                    value={state.minimumFitScore}
                  />
                </label>
              </div>
            </section>

            <div className="onboarding-form__footer">
              <button className="onboarding-submit" disabled={isPending} type="submit">
                {isPending ? "저장 중..." : "저장 후 대시보드로"}
              </button>
              <p className={["onboarding-status", `onboarding-status--${status.tone}`].join(" ")}>
                {status.message}
              </p>
            </div>
          </div>

          <aside className="onboarding-mockup__aside">
            <div className="onboarding-preview-card">
              <span className="dashboard-kicker">추천 기준</span>
              <h3 className="dashboard-section__title">추천 기준 요약</h3>
              <div className="onboarding-preview-card__group">
                <span className="dashboard-detail__label">핵심 조합</span>
                <p className="onboarding-preview-card__text">
                  {state.selectedRoles.length > 0
                    ? roleOptions
                        .filter((option) => state.selectedRoles.includes(option.id))
                        .map((option) => option.label)
                        .join(", ")
                    : "아직 선택한 직무가 없습니다."}
                </p>
                <p className="onboarding-preview-card__text">
                  {state.selectedSeniority.length > 0
                    ? seniorityOptions
                        .filter((option) => state.selectedSeniority.includes(option.id))
                        .map((option) => option.label)
                        .join(", ")
                    : "아직 선택한 경력 레벨이 없습니다."}
                </p>
              </div>
              <div className="onboarding-preview-card__group">
                <span className="dashboard-detail__label">중요 스킬</span>
                <p className="onboarding-preview-card__text">
                  {[
                    ...skillOptions
                      .filter((option) => state.selectedSkills.includes(option.id))
                      .map((option) => option.label),
                    ...state.customSkills,
                  ].join(", ") || "아직 선택한 스킬이 없습니다."}
                </p>
              </div>
              <div className="onboarding-preview-card__group">
                <span className="dashboard-detail__label">선호 팀 맥락</span>
                <p className="onboarding-preview-card__text">
                  {state.selectedTeamContexts.length > 0
                    ? teamContextOptions
                        .filter((option) => state.selectedTeamContexts.includes(option.id))
                        .map((option) => option.label)
                        .join(", ")
                    : "아직 선택한 팀 맥락이 없습니다."}
                </p>
              </div>
              {selectedComparisons.length > 0 ? (
                <div className="onboarding-preview-card__group">
                  <span className="dashboard-detail__label">세부 선호</span>
                  <ul className="onboarding-preview-card__list">
                    {selectedComparisons.map((prompt) => (
                      <li key={prompt.id}>
                        {scaleValueToLabel.get(state.comparisonState[prompt.id] ?? 99)}:{" "}
                        {prompt.leftLabel} / {prompt.rightLabel}
                      </li>
                    ))}
                  </ul>
                </div>
              ) : null}
              <div className="onboarding-preview-card__group">
                <span className="dashboard-detail__label">빠른 제외 조건</span>
                <p className="onboarding-preview-card__text">
                  {[
                    ...exclusionOptions
                      .filter((option) => state.selectedExclusions.includes(option.id))
                      .map((option) => option.label),
                    ...state.customExclusions,
                  ].join(", ") || "아직 선택한 제외 조건이 없습니다."}
                </p>
              </div>
              <div className="onboarding-preview-card__group">
                <span className="dashboard-detail__label">보조 메모</span>
                <p className="onboarding-preview-card__text">
                  {state.note.trim().length > 0 ? state.note : "None"}
                </p>
              </div>
            </div>
          </aside>
        </div>
      </form>
    </section>
  );
}
