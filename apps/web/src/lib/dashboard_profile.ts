import type { UserProfileResponse } from "@/lib/profile_types";

type DashboardProfileSource = Pick<
  UserProfileResponse,
  "profile_data" | "guidelines" | "preferences" | "notification_settings"
>;

const workModeLabels: Record<string, string> = {
  remote: "원격",
  hybrid: "하이브리드",
  onsite: "상주 출근",
};

const locationLabels: Record<string, string> = {
  seoul: "서울",
  pangyo: "판교",
  bundang: "분당",
  gyeonggi: "경기권",
  daejeon: "대전",
  busan: "부산",
  nationwide: "전국 어디든",
  global: "해외 포함",
};

const teamContextLabels: Record<string, string> = {
  "ai-first": "AI/ML 팀이 핵심 조직",
  "product-team": "프로덕트와 가까운 역할",
  "platform-team": "플랫폼/인프라와 맞닿은 역할",
  "small-team": "작은 팀에서 폭넓게 담당",
  "specialist-team": "전문성 높은 팀 분업",
};

const skillLabels: Record<string, string> = {
  python: "Python",
  sql: "SQL",
  pytorch: "PyTorch",
  tensorflow: "TensorFlow",
  llm: "LLM application",
  rag: "RAG",
  evaluation: "LLM evaluation",
  airflow: "Airflow / orchestration",
  mlops: "MLOps / serving",
  aws: "AWS / cloud",
  backend: "Backend API",
  analytics: "Experimentation / analytics",
};

const exclusionLabels: Record<string, string> = {
  contract: "계약직 중심",
  internship: "인턴 포지션",
  "onsite-only": "상주 출근만 가능",
  "research-heavy": "리서치 성향이 너무 강함",
  "no-llm": "LLM 업무가 전혀 없음",
  "korean-required": "한국어 필수",
  "visa-none": "비자 지원 없음",
};

const comparisonLabels: Record<string, [string, string]> = {
  "delivery-vs-research": ["모델 개발 중심", "서비스 적용 중심"],
  "company-shape": ["작은 팀 자율성", "큰 조직 안정성"],
  "llm-vs-classic": ["LLM 응용 중심", "전통 ML 중심"],
  "ownership-shape": ["한 문제를 깊게 파는 역할", "여러 영역을 넓게 맡는 역할"],
  "speed-vs-process": ["빠른 실행과 실험", "정교한 프로세스와 안정성"],
  "build-vs-operate": ["새 시스템 구축 비중", "운영 최적화 비중"],
};

const comparisonToneLabels: Record<number, string> = {
  [-2]: "강하게 왼쪽",
  [-1]: "약하게 왼쪽",
  [0]: "중립",
  [1]: "약하게 오른쪽",
  [2]: "강하게 오른쪽",
};

export type DashboardProfileSummary = {
  role: string;
  yearsOfExperience: number;
  preferredSkills: string[];
  exclusions: string[];
  workModes: string[];
  locations: string[];
  teamContexts: string[];
  comparisonTones: string[];
  note: string | null;
  minimumFitScore: number;
};

export function deriveDashboardProfileSummary(profile: DashboardProfileSource): DashboardProfileSummary {
  const preferences = profile.preferences;

  const preferredSkills = [
    ...expandIds(preferences.skills.preset, skillLabels),
    ...normalizeList(preferences.skills.custom),
  ];
  const exclusions = [
    ...expandIds(preferences.exclusions.preset, exclusionLabels),
    ...normalizeList(preferences.exclusions.custom),
  ];

  return {
    role: profile.profile_data.role.trim(),
    yearsOfExperience: profile.profile_data.years_of_experience,
    preferredSkills:
      preferredSkills.length > 0 ? preferredSkills : normalizeList(profile.guidelines.must_haves),
    exclusions: exclusions.length > 0 ? exclusions : normalizeList(profile.guidelines.deal_breakers),
    workModes: expandIds(preferences.work_modes, workModeLabels),
    locations: expandIds(preferences.locations, locationLabels),
    teamContexts: expandIds(preferences.team_contexts, teamContextLabels),
    comparisonTones: Object.entries(preferences.comparisons)
      .map(([key, value]) => {
        const labels = comparisonLabels[key];
        const tone = comparisonToneLabels[value];
        if (!labels || tone === undefined) {
          return "";
        }
        return `${tone}: ${labels[0]} / ${labels[1]}`;
      })
      .filter(Boolean),
    note: preferences.note?.trim() || null,
    minimumFitScore: profile.notification_settings.minimum_fit_score,
  };
}

function expandIds(values: string[], mapping: Record<string, string>) {
  return normalizeList(values).map((value) => mapping[value] ?? value);
}

function normalizeList(values: string[]) {
  return values.map((value) => value.trim()).filter(Boolean);
}
