## 검증 전략과 TODO 반영 원칙

### 회귀 기준선

- existing PromptOps/context/implementation docs/pipeline 테스트를 regression baseline으로 유지합니다.
- 외부 API shape는 이번 migration 초기에 변경하지 않습니다.
- LangSmith experiment flow는 보호 대상입니다.

### 추가해야 할 검증

- task routing fixture tests
- context bundle fixture tests
- assistant hook parity smoke tests
- domain runner dry-run tests

### acceptance 시나리오

- PromptOps task는 PromptOps context와 validation만 자동 선택
- Scraper task는 parser/selectors/fixtures 중심 context만 선택
- Front task는 `apps/web` surface를 기본 소유
- Back task는 API/service/runtime contract를 기본 소유
- 동일 task spec을 Codex와 Claude가 거의 같은 의미로 해석

### TODO.md 반영 원칙

- `TODO.md`는 active plan package 인덱스 역할만 유지합니다.
- 긴 migration 설명은 이 package가 canonical source가 됩니다.
- `TODO.md`에는 새 active plan 링크와 milestone snapshot만 노출합니다.
- 이후 세부 구현 task는 이 package를 parent context로 삼아 별도 active plan으로 분기합니다.

### 후속 구현 순서 제안

1. `.agents/` canonical 구조 도입 plan
2. capability pack / task routing plan
3. PromptOps decoupling 및 prompt ownership 이동 plan
4. shared hook parity 및 runner 도입 plan
5. live status surface 전환 plan

### 작업 메모

- 현재 active package는 migration 방향을 고정하는 coordination 문서입니다.
- 실제 구현은 별도 worktree와 별도 execution session에서 잘게 쪼개 진행합니다.
