<!-- 신규 규칙: 스크래퍼 도메인 -->

# 스크래퍼 규칙

## 아키텍처

- `BaseScraperSource` 프로토콜을 준수한다 (`async fetch_jobs(user_context) → List[ScrapedJob]`).
- `ScraperRegistry`를 통해 소스를 등록하고 발견한다.
- 소스별 구현은 `src/scraper/sources/<platform>/`에 격리한다.
- `normalizers/job_normalizer.py`로 플랫폼 무관 정규화를 수행한다.

## 소스별 격리

- 한 소스의 오류가 다른 소스를 오염시키지 않도록 격리한다.
- 스크래퍼 실패는 파이프라인을 중단시키지 않고 건너뛰고 기록한다.
- 각 소스는 독립적으로 테스트 가능해야 한다.

## 현재 구현 상태

- 실제 소스: Incruit (`sources/incruit/`) -- Playwright 기반
- 테스트 소스: MockPlatform (`sources/mock_platform/`)
- **레지스트리 패턴이 단일 소스로만 검증됨** -- 2번째 소스 구현 시 추상화 검증 필요

## 설정

- `SCRAPER_MAX_PAGES` -- 페이지네이션 제한
- `SCRAPER_HEADLESS` -- 헤드리스 브라우저 모드 (기본: true)
- `SCRAPER_TIMEOUT_MS` -- 타임아웃 (밀리초)
- 설정은 루트 `.env` 파일에서 로드

## 테스트 지침

- 고정 데이터(fixture) 기반 파싱 테스트를 선호한다.
- 필요한 경우만 소수의 안전장치가 마련된 실시간 검사를 추가한다.
- 중복 제거 동작에 대한 회귀 테스트를 유지한다.
