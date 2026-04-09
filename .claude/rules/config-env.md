<!-- AGENTS.md 추출: 환경 분리, 구성 및 환경 변수 규칙 -->

# 설정 및 환경 변수 규칙

## 환경 분리

dev와 prod에 대해 명시적으로 분리한다:
- 별도의 Supabase 프로젝트
- 별도의 Slack 워크스페이스/앱 자격 증명
- 별도의 OAuth 자격 증명
- 별도의 API 키와 시크릿
- 기본적으로 로컬이 prod를 가리키지 않도록 한다

운영 규칙:
- dev 환경은 테스트, 디버깅, 스크래퍼 반복에 안전해야 한다.
- 예약된 전송(scheduled delivery)은 prod에서만 실행한다 (`ALLOW_DEV_SCHEDULE` 없이는).

## 구성 로딩

- `src/common/config.py`에서 중앙집중화, Pydantic Settings 사용
- 환경 변수를 한 번만 읽고, 조기에 검증, 타입이 지정된 설정 객체 노출
- prod 직면 코드 경로에서 필수 시크릿 누락 시 즉시 실패(fail fast)
- 로컬 기본값은 최소한으로 안전하게 유지

## 명명 규칙

- 모든 환경 변수: 대문자 스네이크 케이스 (`UPPER_SNAKE_CASE`)
- 하위 시스템 접두사: `SUPABASE_*`, `GOOGLE_*`, `SLACK_*`, `LANGSMITH_*`, `GEMINI_*`, `SCRAPER_*`
- 활성 런타임 환경: `APP_ENV` (값: `development`, `test`, `production`)
- 분리된 env 파일 선호: `.env.development`, `.env.test`, `.env.production`

## 현재 데이터 접근 계층 (이중 구조 주의)

현재 PoC는 두 가지 데이터 접근 경로가 공존:
- **Supabase Data API** (기본 PoC 런타임) -- `SUPABASE_SERVICE_ROLE_KEY` 사용
- **SQLModel + Alembic** (레거시 스키마 참조/마이그레이션 기록용)

새 영속성 작업에는 Supabase Data API 경로를 선호한다.
`DATABASE_URL`은 레거시 선택적 툴링 값으로 취급 (기본 런타임 시크릿 아님).

## 시크릿 처리

- 절대 시크릿을 하드코딩하지 않는다.
- 실제 `.env` 파일을 git에 커밋하지 않는다 (`.env.example`만).
- prod 시크릿을 dev/test에서 재사용하지 않는다.
- `SUPABASE_SERVICE_ROLE_KEY`, 웹훅 서명 시크릿은 높은 민감도로 취급한다.
- `NEXT_PUBLIC_*` 값은 `apps/web/.env.*`에만 위치 (시크릿에 이 접두사 금지).
