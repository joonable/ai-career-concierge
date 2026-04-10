# Iteration 003 Report
- **Date:** 2026-03-31 17:08:35
- **Description:** Automated iteration run
- **Pass Rate:** 0.0% (0/10)
- **LangSmith Project:** iter-003-ba18e5c7

## Summary
10개의 케이스에서 실패가 발생했습니다. 아래 상세 내용을 확인하세요.

## Failure Analysis (Annotation Queue Candidate)
| Scenario | Job Title | Failed Rules | Reasoning Snippet |
| :--- | :--- | :--- | :--- |
| Unknown | None | transferable_skill_credit: expected=HIGH, actual=MEDIUM<br>role_alignment_match: expected=MEDIUM, actual=LOW<br>confidence_alignment: expected=MEDIUM, actual=HIGH<br>concern_keywords_match: expected=['mlops', 'deployment', 'serving'], actual='목표 직무와 역할 정렬성이 낮음 (데이터 엔지니어링 중심) MLOps 필수 조건 충족 여부 불확실 모델 배포 오너십 경험 부족 명시' | N/A (Run Failed/Incomplete)... |
| Unknown | None | must_have_coverage_match: expected=PARTIAL, actual=STRONG<br>confidence_alignment: expected=MEDIUM, actual=HIGH<br>concern_keywords_match: expected=['modeling', 'training'], actual='직무명이 '시니어 백엔드 엔지니어'로, MLE 역할의 핵심 ownership이 명확하지 않음 ML 모델 자체 개발 또는 연구 관련 내용은 언급되지 않음' | N/A (Run Failed/Incomplete)... |
| Unknown | None | transferable_skill_credit: expected=HIGH, actual=MEDIUM<br>fit_score_band: fit_score=50, expected_range=(60, 79)<br>concern_keywords_match: expected=['sql', 'modeling', 'scope'], actual='핵심 must-have인 MLOps 경험 불명확 ML Engineer 역할과의 직접적인 정렬성 낮음 SQL이 핵심 기술이 아니라는 점 명시'<br>strength_keywords_match: expected=['python', 'platform', 'inference'], actual='Python 경험 보유 SQL 경험 보유 (핵심은 아님) AI 런타임 인프라 구축 관련성'<br>confidence_alignment: expected=MEDIUM, actual=HIGH | 백엔드 플랫폼 엔지니어 역할은 Machine Learning Engineer와 일부 기술 스택이 겹치지만, 핵심 책임 영역이 다릅니다. Python 경험은 있으나 MLOps 및 A... |
| Unknown | None | strength_keywords_match: expected=['python', 'ranking', 'experimentation'], actual='오프라인 모델링 및 실험 경험 보유 Python 및 SQL 관련 경험 가능성'<br>confidence_alignment: expected=MEDIUM, actual=HIGH<br>concern_keywords_match: expected=['sql', 'mlops', 'ownership'], actual='MLOps 및 프로덕션 서빙에 대한 직접적인 책임 없음 (별도 팀 담당) 핵심 Must-have 중 MLOps 불충족 역할 정렬이 직접적인 MLE와는 다소 차이 있음'<br>fit_score_band: fit_score=55, expected_range=(60, 79) | 직무명은 다르지만, 오프라인 모델링 및 실험 경험은 관련성이 있습니다. 그러나 MLOps 및 프로덕션 서빙에 대한 직접적인 책임이 없다는 점이 주요 우려 사항입니다. Must-ha... |
| Unknown | None | concern_keywords_match: expected=['production', 'mlops', 'ownership'], actual='프로덕션 시스템 책임 거의 없음 (MLOps 필수 조건 불충족) SQL 사용 가볍다고 명시 (SQL 필수 조건 불충족) ML 엔지니어링의 핵심인 배포 및 운영 경험 부족 가능성 높음'<br>must_have_expectation: expected=['Python'], actual_text=''<br>strength_keywords_match: expected=['python', 'personalization', 'modeling'], actual='랭킹 모델 연구 및 실험 분석 경험 (잠재적 transferable skill)'<br>confidence_alignment: expected=MEDIUM, actual=HIGH<br>role_alignment_match: expected=MEDIUM, actual=LOW | 해당 공고는 리서치 사이언티스트 역할로, 머신러닝 엔지니어링의 핵심인 프로덕션 시스템 책임 및 MLOps 경험이 부족합니다. SQL 사용도 가볍다고 명시되어 있어 필수 조건 충족이... |
| Unknown | None | concern_keywords_match: expected=['mlops', 'serving', 'lifecycle'], actual='목표 직무(MLE)와 직접적인 연관성이 낮음 모델 서빙 책임이 없다고 명시됨 MLOps 관련 경험 명시 부족 핵심 MLE 기술 스택(예: 모델 개발, 서빙, 모니터링)에 대한 직접적인 경험 불확실'<br>confidence_alignment: expected=MEDIUM, actual=HIGH<br>role_alignment_match: expected=MEDIUM, actual=LOW | MLE 역할과 직접적인 연관성은 낮으나, Python/SQL 경험 및 실험 인프라 구축 경험은 일부 transferable skill로 작용할 수 있습니다. 모델 서빙 책임이 없다... |
| Unknown | None | confidence_alignment: expected=MEDIUM, actual=HIGH<br>transferable_skill_credit: expected=HIGH, actual=MEDIUM<br>role_alignment_match: expected=MEDIUM, actual=HIGH | MLOps 엔지니어 역할에 대한 높은 적합도를 보입니다. Python, MLOps 경험은 필수 조건과 잘 부합하지만, SQL 경험이 명시되지 않아 검토가 필요합니다. 계약 형태나 ... |
| Unknown | None | concern_keywords_match: expected=['mlops', 'serving', 'title'], actual='직무명이 Machine Learning Engineer와 직접적으로 일치하지 않음 MLOps 경험의 실제 적용 범위 및 책임 소재 불분명 ('배포 책임 없음') 핵심 must-have인 MLOps에 대한 명확한 ownership 부재'<br>strength_keywords_match: expected=['python', 'sql', 'platform'], actual='Python 및 SQL 경험 보유 ML 의사결정 지원이라는 목표에 대한 간접적 기여 가능성' | 채용 공고의 직무명이 '분석 엔지니어'로 MLE와 직접적인 연관성이 낮고, '배포 책임 없음' 명시로 MLOps 경험의 활용 범위가 제한적입니다. Python, SQL 경험은 있으... |
| Unknown | None | must_have_coverage_match: expected=WEAK, actual=PARTIAL<br>strength_keywords_match: expected=['python', 'tooling', 'workflow'], actual='Python 서비스 개발 경험 추론 API 및 배포 파이프라인 운영 경험'<br>confidence_alignment: expected=MEDIUM, actual=HIGH<br>transferable_skill_credit: expected=HIGH, actual=MEDIUM<br>concern_keywords_match: expected=['sql', 'deployment', 'scope'], actual='MLOps 필수 조건 충족 여부 불명확 모델 학습 자체는 리서치 팀 담당으로 ML 엔지니어링의 핵심 영역(모델 개발/개선)과 거리가 있을 수 있음 SQL 필수 조건 언급 없음' | Python 백엔드 경험과 ML 관련 인프라 운영 경험이 일부 겹치지만, 핵심 ML 엔지니어링 역할보다는 모델 서빙 및 배포 파이프라인 운영에 초점이 맞춰져 있습니다. 필수 조건 ... |
| Unknown | None | strength_keywords_match: expected=['python', 'sql', 'deployment'], actual='Python, SQL, MLOps 필수 기술 스택 완벽 충족 머신러닝 플랫폼 구축 경험 모델링 팀과의 협업 경험 6년차 경력으로 요구사항 충족' | 머신러닝 플랫폼 구축 경험과 Python, SQL, MLOps 필수 기술 스택이 목표 직무와 매우 잘 부합합니다. 경력 연차 또한 적합하며, 명확한 결격 사유가 없어 강한 추천 대... |

## Action Items
- [ ] 실패한 케이스에 대해 프롬프트 가이드라인 보완
- [ ] LangSmith Annotation Queue에서 정답(Ground Truth) 재검토
