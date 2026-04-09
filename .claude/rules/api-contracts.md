<!-- AGENTS.md 추출: 필수 외부 인터페이스, API 변경 규칙, 인증 경계 -->

# API 계약 규칙

## 필수 외부 인터페이스

다음 엔드포인트와의 호환성을 유지한다:

| 엔드포인트 | 설명 | 인증 |
|-----------|------|------|
| `POST /api/v1/pipeline/trigger` | 파이프라인 실행 트리거 | `X-API-Key` (내부) |
| `POST /api/v1/slack/interactive-webhook` | Slack 피드백 웹훅 | Slack HMAC 서명 |
| `GET /api/v1/users/me/dashboard` | 대시보드 데이터 | Supabase JWT Bearer |
| `POST /api/v1/evaluations` | 피드백 제출 | Supabase JWT Bearer |

## 인증 경계

- 웹 앱: Next.js SSR → Supabase Google OAuth → 세션 쿠키
- 백엔드: `Authorization: Bearer <Supabase access token>` → JWKS 검증 → 사용자 ID 추출
- 파이프라인 트리거: `X-API-Key` 검증 (GitHub Actions cron)
- Slack 웹훅: HMAC 서명 검증
- 백엔드 영속성: `SUPABASE_SERVICE_ROLE_KEY`와 Supabase Data API

## API 변경 규칙

- 요청/응답 스키마, 인증 동작, 웹훅 페이로드, 상태 enum을 퍼블릭 계약으로 취급한다.
- API 계약 변경 시 타입 스키마, 핸들러, 문서, 테스트를 같은 변경에서 업데이트한다.
- 브레이킹 체인지는 최종 요약에서 명시적으로 언급한다.
- 변경 확정 전에 대시보드, Slack 연동, 스케줄러 트리거, 저장된 평가 데이터에 미치는 하위 영향을 확인한다.
