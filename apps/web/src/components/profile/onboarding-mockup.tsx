"use client";

import React, { useState } from "react";

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

const comparisonScale = [
  "강하게 왼쪽",
  "약하게 왼쪽",
  "중립",
  "약하게 오른쪽",
  "강하게 오른쪽",
] as const;

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

const scaleIndexToLabel = new Map<number, string>(
  comparisonScale.map((label, index) => [index, label]),
);

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

function normalizeKeyword(value: string) {
  return value.trim().replace(/\s+/g, " ");
}

function addKeyword(
  rawValue: string,
  current: string[],
  setter: React.Dispatch<React.SetStateAction<string[]>>,
  clear: () => void,
) {
  const normalized = normalizeKeyword(rawValue);

  if (!normalized) {
    return;
  }

  setter((previous) =>
    previous.some((item) => item.toLowerCase() === normalized.toLowerCase())
      ? previous
      : [...previous, normalized],
  );
  clear();
}

function removeKeyword(
  keyword: string,
  setter: React.Dispatch<React.SetStateAction<string[]>>,
) {
  setter((previous) => previous.filter((item) => item !== keyword));
}

export function OnboardingMockup() {
  const [roles, setRoles] = useState<string[]>(["ml-engineer", "llm-engineer"]);
  const [seniority, setSeniority] = useState<string[]>(["senior"]);
  const [workModes, setWorkModes] = useState<string[]>(["hybrid", "remote"]);
  const [locations, setLocations] = useState<string[]>(["seoul", "pangyo"]);
  const [teamContexts, setTeamContexts] = useState<string[]>(["ai-first", "product-team"]);
  const [skills, setSkills] = useState<string[]>(["python", "llm", "evaluation", "backend"]);
  const [customSkills, setCustomSkills] = useState<string[]>(["LangGraph", "Vector DB"]);
  const [skillInput, setSkillInput] = useState("");
  const [exclusions, setExclusions] = useState<string[]>(["contract", "internship", "onsite-only"]);
  const [customExclusions, setCustomExclusions] = useState<string[]>(["논문 실적 필수"]);
  const [exclusionInput, setExclusionInput] = useState("");
  const [comparisonState, setComparisonState] = useState<Record<string, number>>({
    "delivery-vs-research": 1,
    "company-shape": 0,
    "llm-vs-classic": 0,
    "ownership-shape": 2,
    "speed-vs-process": 1,
    "build-vs-operate": 3,
  });
  const [isAdvancedOpen, setIsAdvancedOpen] = useState(false);
  const [note, setNote] = useState(
    "텍스트 입력은 꼭 필요한 보충 설명만 받도록 마지막에 짧게 남깁니다.",
  );

  const toggleSelection = (
    id: string,
    setter: React.Dispatch<React.SetStateAction<string[]>>,
  ) => {
    setter((previous) =>
      previous.includes(id) ? previous.filter((item) => item !== id) : [...previous, id],
    );
  };

  const completedSections = [
    roles.length > 0,
    seniority.length > 0,
    workModes.length > 0 || locations.length > 0,
    skills.length + customSkills.length > 0,
    isAdvancedOpen,
  ].filter(Boolean).length;

  const summaryLines = [
    `${roles.length}개 직무 카드 선택`,
    `${seniority.length}개 경력 레벨 선택`,
    `${workModes.length}개 근무 형태 + ${locations.length}개 지역`,
    `${skills.length + customSkills.length}개 핵심 스킬`,
    `${exclusions.length + customExclusions.length}개 제외 조건`,
  ];

  return (
    <>
      <section className="dashboard-grid onboarding-page__grid onboarding-mockup__hero-grid">
        <article className="dashboard-card dashboard-card--active dashboard-card--span-2 onboarding-hero-card">
          <div className="dashboard-hero">
            <div className="dashboard-hero__copy">
              <span className="dashboard-kicker">Onboarding Mockup</span>
              <h1 className="dashboard-title onboarding-page__title">텍스트 대신 선택으로 기준을 빠르게 맞춥니다</h1>
              <p className="dashboard-subcopy">
                새 화면은 자유 입력을 뒤로 내리고, 실제 공고에서 판별 가능한 신호를 중심으로
                선호를 고르게 구성했습니다.
              </p>
            </div>
            <div className="dashboard-chip-list">
              <span className="dashboard-chip">직무 카드</span>
              <span className="dashboard-chip">핵심 스킬</span>
              <span className="dashboard-chip">빠른 제외 조건</span>
              <span className="dashboard-chip">고급 설정</span>
              <span className="dashboard-chip dashboard-chip--muted">Front-end mock only</span>
            </div>
          </div>
        </article>
        <article className="dashboard-card onboarding-page__summary">
          <div className="dashboard-summary__header">
            <div className="dashboard-summary-card__copy">
              <span className="dashboard-kicker">Prototype</span>
              <h2 className="dashboard-section__title">구성 상태</h2>
            </div>
            <span className="dashboard-pill dashboard-pill--accent">{completedSections}/5 준비</span>
          </div>
          <div className="dashboard-checklist" role="list">
            {summaryLines.map((line) => (
              <div className="dashboard-checklist__item dashboard-checklist__item--complete" key={line}>
                <span className="dashboard-checklist__status" aria-hidden="true">
                  <span className="dashboard-checklist__dot dashboard-checklist__dot--complete" />
                </span>
                <div className="dashboard-checklist__copy">
                  <span className="dashboard-detail__label">{line}</span>
                  <p className="dashboard-checklist__meta">선택형 입력으로 바로 조정 가능</p>
                </div>
              </div>
            ))}
          </div>
        </article>
      </section>

      <section className="dashboard-card onboarding-form-card onboarding-mockup">
        <div className="onboarding-form__header">
          <div className="dashboard-summary-card__copy">
            <span className="dashboard-kicker">Step 1</span>
            <h2 className="dashboard-section__title">목표 프로필을 선택형으로 구성</h2>
          </div>
          <span className="dashboard-pill">No backend</span>
        </div>

        <div className="onboarding-mockup__layout">
          <div className="onboarding-mockup__main">
            <ToggleGroup
              label="보고 싶은 직무"
              onToggle={(id) => toggleSelection(id, setRoles)}
              options={roleOptions}
              selected={roles}
            />
            <ToggleGroup
              label="경력 레벨"
              onToggle={(id) => toggleSelection(id, setSeniority)}
              options={seniorityOptions}
              selected={seniority}
              helper="연차 감각을 함께 보여줘서 어떤 수준을 눌러야 할지 덜 헷갈리게 합니다."
            />
            <ToggleGroup
              label="근무 형태"
              onToggle={(id) => toggleSelection(id, setWorkModes)}
              options={workModeOptions}
              selected={workModes}
              helper="출근 조건은 hard filter로 이어지기 쉬워서 초반에 빠르게 받습니다."
            />
            <ToggleGroup
              label="지역"
              onToggle={(id) => toggleSelection(id, setLocations)}
              options={locationOptions}
              selected={locations}
              helper="국내 주요 선택지를 넓히고, 실제 탐색 범위를 한국어로 바로 이해하게 구성했습니다."
            />
            <ToggleGroup
              label="일하고 싶은 팀 맥락"
              onToggle={(id) => toggleSelection(id, setTeamContexts)}
              options={teamContextOptions}
              selected={teamContexts}
              helper="막연한 회사 단계 대신, JD에서 체감되는 팀 성격을 더 구체적으로 고릅니다."
            />

            <section className="onboarding-mockup__block">
              <div className="onboarding-mockup__block-header">
                <div>
                  <span className="dashboard-detail__label">빠르게 제외할 조건</span>
                  <p className="onboarding-mockup__helper">
                    JD에서 비교적 확인 가능한 조건만 두고, 추상적인 항목은 뺐습니다.
                  </p>
                </div>
              </div>
              <div className="onboarding-choice-grid" role="list" aria-label="빠르게 제외할 조건">
                {exclusionOptions.map((option) => {
                  const isSelected = exclusions.includes(option.id);
                  return (
                    <button
                      aria-pressed={isSelected}
                      className={[
                        "onboarding-choice-chip",
                        "onboarding-choice-chip--danger",
                        isSelected ? "onboarding-choice-chip--selected" : "",
                      ].join(" ")}
                    key={option.id}
                    onClick={() => toggleSelection(option.id, setExclusions)}
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
                      addKeyword(exclusionInput, customExclusions, setCustomExclusions, () =>
                        setExclusionInput(""),
                      );
                    }
                  }}
                  placeholder="직접 제외 키워드 추가, 예: 박사 학위 필수"
                  value={exclusionInput}
                />
                <button
                  className="onboarding-inline-button"
                  onClick={() =>
                    addKeyword(exclusionInput, customExclusions, setCustomExclusions, () =>
                      setExclusionInput(""),
                    )
                  }
                  type="button"
                >
                  추가
                </button>
              </div>
              <div className="onboarding-choice-grid" role="list" aria-label="직접 입력한 제외 키워드">
                {customExclusions.map((keyword) => (
                  <button
                    className="onboarding-choice-chip onboarding-choice-chip--selected onboarding-choice-chip--danger"
                    key={keyword}
                    onClick={() => removeKeyword(keyword, setCustomExclusions)}
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
                    JD relevance를 좌우하는 핵심 신호라서 preset과 직접 입력을 같이 지원합니다.
                  </p>
                </div>
              </div>
              <div className="onboarding-choice-grid" role="list" aria-label="중요하게 볼 스킬">
                {skillOptions.map((option) => {
                  const isSelected = skills.includes(option.id);
                  return (
                    <button
                      aria-pressed={isSelected}
                      className={[
                        "onboarding-choice-chip",
                        isSelected ? "onboarding-choice-chip--selected" : "",
                      ].join(" ")}
                      key={option.id}
                      onClick={() => toggleSelection(option.id, setSkills)}
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
                      addKeyword(skillInput, customSkills, setCustomSkills, () => setSkillInput(""));
                    }
                  }}
                  placeholder="직접 스킬 키워드 추가, 예: Spark, 추천 시스템, LangChain"
                  value={skillInput}
                />
                <button
                  className="onboarding-inline-button"
                  onClick={() => addKeyword(skillInput, customSkills, setCustomSkills, () => setSkillInput(""))}
                  type="button"
                >
                  추가
                </button>
              </div>
              <div className="onboarding-choice-grid" role="list" aria-label="직접 입력한 스킬">
                {customSkills.map((keyword) => (
                  <button
                    className="onboarding-choice-chip onboarding-choice-chip--selected"
                    key={keyword}
                    onClick={() => removeKeyword(keyword, setCustomSkills)}
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
              onToggle={(event) => setIsAdvancedOpen((event.currentTarget as HTMLDetailsElement).open)}
            >
              <summary className="onboarding-advanced__summary">
                <div>
                  <span className="dashboard-detail__label">고급 설정</span>
                  <p className="onboarding-mockup__helper">
                    기본 선택만으로 부족할 때 펼쳐서 더 세밀한 선호 톤을 조정합니다.
                  </p>
                </div>
                <span className="dashboard-pill">{isAdvancedOpen ? "접기" : "펼치기"}</span>
              </summary>
              <div className="onboarding-advanced__content">
                <div className="onboarding-comparison-list">
                  {comparisonPrompts.map((prompt) => (
                    <article className="onboarding-comparison-card" key={prompt.id}>
                      <div className="onboarding-comparison-card__copy">
                        <p className="dashboard-detail__label">
                          {prompt.leftLabel} vs {prompt.rightLabel}
                        </p>
                        <p className="onboarding-mockup__helper">{prompt.description}</p>
                      </div>
                      <div className="onboarding-comparison-scale" role="group" aria-label={prompt.description}>
                        {comparisonScale.map((optionLabel, index) => {
                          const isSelected = comparisonState[prompt.id] === index;
                          return (
                            <button
                              aria-pressed={isSelected}
                              className={[
                                "onboarding-scale-button",
                                isSelected ? "onboarding-scale-button--selected" : "",
                              ].join(" ")}
                              key={optionLabel}
                              onClick={() =>
                                setComparisonState((current) => ({ ...current, [prompt.id]: index }))
                              }
                              type="button"
                            >
                              {optionLabel}
                            </button>
                          );
                        })}
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
                    텍스트 입력은 마지막에 짧게만 남기고, 기본 온보딩은 선택으로 끝내는 흐름입니다.
                  </p>
                </div>
              </div>
              <textarea
                className="onboarding-field__input onboarding-field__textarea"
                name="mockupNote"
                onChange={(event) => setNote(event.target.value)}
                value={note}
              />
            </section>
          </div>

          <aside className="onboarding-mockup__aside">
            <div className="onboarding-preview-card">
              <span className="dashboard-kicker">Preview</span>
              <h3 className="dashboard-section__title">이렇게 해석됩니다</h3>
              <div className="onboarding-preview-card__group">
                <span className="dashboard-detail__label">핵심 조합</span>
                <p className="onboarding-preview-card__text">
                  {roles.length > 0 ? roleOptions.filter((option) => roles.includes(option.id)).map((option) => option.label).join(", ") : "직무 미선택"}
                </p>
                <p className="onboarding-preview-card__text">
                  {seniority.length > 0
                    ? seniorityOptions
                        .filter((option) => seniority.includes(option.id))
                        .map((option) => option.label)
                        .join(", ")
                    : "경력 레벨 미선택"}
                </p>
              </div>
              <div className="onboarding-preview-card__group">
                <span className="dashboard-detail__label">중요 스킬</span>
                <p className="onboarding-preview-card__text">
                  {[...skillOptions
                    .filter((option) => skills.includes(option.id))
                    .map((option) => option.label), ...customSkills].join(", ") || "아직 선택한 스킬이 없습니다."}
                </p>
              </div>
              <div className="onboarding-preview-card__group">
                <span className="dashboard-detail__label">선호 팀 맥락</span>
                <p className="onboarding-preview-card__text">
                  {teamContexts.length > 0
                    ? teamContextOptions
                        .filter((option) => teamContexts.includes(option.id))
                        .map((option) => option.label)
                        .join(", ")
                    : "아직 선택한 팀 맥락이 없습니다."}
                </p>
              </div>
              <div className="onboarding-preview-card__group">
                <span className="dashboard-detail__label">비교 선택 요약</span>
                {isAdvancedOpen ? (
                  <ul className="onboarding-preview-card__list">
                    {comparisonPrompts.map((prompt) => (
                      <li key={prompt.id}>
                        {scaleIndexToLabel.get(comparisonState[prompt.id])}: {prompt.leftLabel} /{" "}
                        {prompt.rightLabel}
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="onboarding-preview-card__text">고급 설정을 펼치면 세부 선호 톤이 여기에 반영됩니다.</p>
                )}
              </div>
              <div className="onboarding-preview-card__group">
                <span className="dashboard-detail__label">빠른 제외 조건</span>
                <p className="onboarding-preview-card__text">
                  {[...exclusionOptions
                    .filter((option) => exclusions.includes(option.id))
                    .map((option) => option.label), ...customExclusions].join(", ") ||
                    "아직 선택한 제외 조건이 없습니다."}
                </p>
              </div>
              <div className="onboarding-preview-card__group">
                <span className="dashboard-detail__label">보조 메모</span>
                <p className="onboarding-preview-card__text">{note}</p>
              </div>
            </div>
          </aside>
        </div>
      </section>
    </>
  );
}
