<!-- 신규 규칙: 프론트엔드 도메인 -->

# 프론트엔드 규칙

## 기술 스택

- Next.js 15 (App Router, React 19)
- TypeScript strict mode
- Supabase SSR 세션 (Google OAuth)
- Vitest + React Testing Library

## App Router 규칙

- 페이지 라우트는 `apps/web/src/app/`에 위치
- 재사용 가능한 UI는 `apps/web/src/components/`에 위치
- 런타임 연동 코드는 `apps/web/src/lib/`에 위치
- 서버/클라이언트 컴포넌트 경계를 명확히 한다

## 인증 패턴

- Next.js SSR에서 Supabase 세션 쿠키를 사용한다.
- 보호된 라우트는 Supabase 세션 쿠키에 의존한다 (커스텀 로컬 인증 상태가 아님).
- 백엔드 호출 시 `Authorization: Bearer <Supabase access token>` 사용.
- `NEXT_PUBLIC_*` 접두사는 공개 값에만 사용, 시크릿에는 절대 사용하지 않는다.

## 현재 라우트

- `/` -- 홈
- `/login` -- Google OAuth 로그인
- `/auth/callback` -- OAuth 콜백
- `/onboarding` -- 프로필 설정
- `/dashboard` -- 메인 대시보드 (추천/피드백)
- `/internal` -- 운영 허브
- `/internal/promptops` -- PromptOps UI
- `/internal/docs` -- 마크다운 문서 뷰어

## PoC 범위 제약

현재 PoC 단계에서 프론트엔드는 최소 기능에 집중한다:
- Three.js, Framer Motion 등 시각 효과는 핵심 기능이 아님 -- 제거 검토 대상
- 추천 검토/피드백을 넘어선 고급 대시보드 기능은 후순위
- 엔드투엔드 PoC 루프가 작동한 후에만 UI 고도화를 진행한다

## 테스트

- Vitest + React Testing Library 사용
- 대시보드 렌더링, 로그인 플로우, 데이터 매핑 로직 중심
- UI 스냅샷은 PoC 단계에서 낮은 우선순위
