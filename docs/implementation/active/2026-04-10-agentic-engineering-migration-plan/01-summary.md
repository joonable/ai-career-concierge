## 요약 및 결정사항

### 목표

이 저장소를 "하네스 없는 ad hoc 협업"에서 "도메인별 전문 서브에이전트가 협업하는 agentic engineering"으로 올리되, 이미 잘 작동하는 자산은 유지합니다.

### 이번 plan의 기본 결정

- canonical control plane은 assistant-neutral core로 둡니다.
- sub-agent routing은 당분간 semi-auto를 기본값으로 둡니다.
- FastAPI / LangGraph / Next.js / PromptOps 현재 스택은 유지합니다.
- 초기 migration에서는 외부 API 응답 shape를 바꾸지 않고 내부 agent contract만 추가합니다.
- `.claude/`, `.gemini/`, Codex 지침은 thin adapter로 수렴시키고, source of truth는 `.agents/` 계층으로 올립니다.

### 기대 결과

- PromptOps / Scraper / Front / Back이 "톤만 다른 assistant persona"가 아니라 입력 계약, 허용 surface, 검증 세트, handoff contract를 가진 전문 runner로 승격됩니다.
- 문서와 스크립트에 흩어진 규칙이 capability pack과 shared hook로 수렴됩니다.
- 같은 task spec을 Codex / Claude가 거의 같은 의미로 해석할 수 있는 운영 기반을 확보합니다.
