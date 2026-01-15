# docs 폴더 정리 계획서

**작성일**: 2026-01-15  
**작성자**: Claude (클로)  
**목적**: 문서 통합 및 불필요 파일 삭제

---

## 📊 현재 상태 분석

### 전체 파일 목록 (33개)
```
AI_MODEL_STRATEGY.md
ARCHITECTURE_PRINCIPLES.md
claude.md
CLAUDE_GUIDE.md
CLAUDE_인수인계_20260115_0940.md
CLAUDE_작업진행서_20260115_0933.md
CODE_REFACTORING_PLAN_20260115.md
CODE_STRUCTURE_ANALYSIS_20260110.md
conversation_001.md
conversation_002_jbody_analysis.md
CURRENT_STATUS.md
DAILY_PLAN_20260115.md
DESIGN_DOCUMENT.md
FINAL_SCHEMA.md
GEMINI_API_ISSUE.md
Gin_2026015_advice.md
HINO_CATEGORY_STRUCTURE.md
IMAGE_AND_EBOOK_PLAN.md
IMPROVEMENT_PLAN.md
JNext.code-workspace
JNEXT_CORE_VISION.md
JNEXT_ROADMAP.md
JNEXT_SUMMARY_20260115.md
JNEXT_V2_IMPLEMENTATION_PLAN.md
JNEXT_VS_HINOBALANCE.md
MEME_PRODUCTION_GUIDE.md
README_AFTERNOON.md
SECURITY_SCHEDULE.md
STRUCTURE.md
STRUCTURE_20260114.md
STRUCTURE_20260114_2150.md
TESTING_CHECKLIST.md
WORK_SUMMARY_20260114_AFTERNOON.md
작업정리_hino_review_hover_fix.md
```

---

## 🗂️ 문서 분류

### A. 핵심 문서 (유지 - 15개)
**프로젝트 비전 & 아키텍처**:
1. `JNEXT_CORE_VISION.md` ⭐ - J님의 핵심 비전 (창의성 저장 + 자동화)
2. `ARCHITECTURE_PRINCIPLES.md` - JNext PaaS 구조 (House/Rooms)
3. `JNEXT_VS_HINOBALANCE.md` - 플랫폼 vs 프로젝트 구분
4. `DESIGN_DOCUMENT.md` - 전체 설계서 (800줄)
5. `STRUCTURE.md` - 최신 구조 설계 (729줄)

**개발 계획**:
6. `JNEXT_ROADMAP.md` - 8단계 파이프라인 (RAW→밈→숏→전자책)
7. `AI_MODEL_STRATEGY.md` - Gemini Pro/Flash, GPT-4o 전략
8. `CODE_REFACTORING_PLAN_20260115.md` ⭐ - 오늘 작성 (리팩터링 계획)
9. `DAILY_PLAN_20260115.md` - 오늘 작업 계획

**콘텐츠 자동화**:
10. `IMAGE_AND_EBOOK_PLAN.md` - 전자책 출판 계획
11. `FINAL_SCHEMA.md` - FINAL 문서 스키마
12. `MEME_PRODUCTION_GUIDE.md` - 밈 제작 프로세스 (J님 설명)
13. `HINO_CATEGORY_STRUCTURE.md` - 카테고리 = 메뉴 자동화

**Claude 인수인계**:
14. `CLAUDE_인수인계_20260115_0940.md` ⭐ - 최신 인수인계 (오늘 아침)
15. `claude.md` - Claude 세션 복구 가이드

---

### B. 중복/통합 대상 (7개 → 2개로 통합)

#### B-1. 구조 설명 중복 (3개 → 1개)
**통합**: `STRUCTURE.md` (최신, 729줄) **유지**

**삭제 대상**:
- ❌ `STRUCTURE_20260114.md` (355줄) - 1일 전 백업, 내용 중복
- ❌ `STRUCTURE_20260114_2150.md` (289줄) - 같은 날 백업, 내용 중복

**이유**: STRUCTURE.md가 가장 최신이고 완전함

---

#### B-2. 작업 요약 중복 (4개 → 1개)
**통합**: 새 파일 `WORK_HISTORY.md` 생성

**통합 대상**:
- `CLAUDE_작업진행서_20260115_0933.md` (527줄) - 오늘 오전 작업
- `WORK_SUMMARY_20260114_AFTERNOON.md` (360줄) - 어제 오후 작업
- `README_AFTERNOON.md` (192줄) - 어제 오후 요약 (중복)
- `JNEXT_SUMMARY_20260115.md` - 오늘 요약

**통합 후 구조**:
```markdown
# JNext 작업 이력

## 2026-01-15 (오전)
- 전자책 폰트 시스템
- DALL-E 이미지 생성
- Firebase Storage 연동

## 2026-01-14 (오후)
- 듀얼 슬라이더 시스템
- 3-Stage Storage
- Hierarchical Firestore

## 2026-01-12
- hino_review.html 호버 효과 수정
```

**삭제**: 원본 4개 파일

---

### C. 대화 기록 (보관 - 2개)
**목적**: 중요한 대화 맥락 보존

1. `conversation_001.md` (1051줄) - 2026-01-12 대화
2. `conversation_002_jbody_analysis.md` (252줄) - 2026-01-14 AI 품질 개선

**보관 이유**: J님과의 핵심 의사결정 과정 기록

---

### D. 레거시/해결된 이슈 (삭제 - 5개)

#### D-1. 해결된 기술 이슈
- ❌ `GEMINI_API_ISSUE.md` - Gemini API 문제 (이미 해결됨)
- ❌ `작업정리_hino_review_hover_fix.md` - 호버 효과 수정 (완료됨)

#### D-2. 참고용 외부 자문
- ❌ `Gin_2026015_advice.md` - 진(GPT-4o)의 조언 (참고만)

#### D-3. 구버전 상태 문서
- ❌ `CURRENT_STATUS.md` - 구버전 상태 (최신 문서로 대체됨)
- ❌ `JNEXT_V2_IMPLEMENTATION_PLAN.md` - v2 구현 계획 (이미 완료)

---

### E. 구버전 분석 (참고 보관 - 2개)
**목적**: 과거 분석 자료 참고용

1. `CODE_STRUCTURE_ANALYSIS_20260110.md` - 2026-01-10 코드 분석
2. `IMPROVEMENT_PLAN.md` - 개선 방안 (일부 여전히 유효)

**보관 이유**: 리팩터링 시 참고 가능

---

### F. 기타 (유지 - 2개)
1. `TESTING_CHECKLIST.md` - 테스트 체크리스트 (유용)
2. `SECURITY_SCHEDULE.md` - 보안 점검 스케줄 (중요)
3. `JNext.code-workspace` - VS Code 워크스페이스 설정

---

## 📝 정리 계획

### Phase 1: 통합 작업

#### 1-1. WORK_HISTORY.md 생성
**통합 대상**:
- CLAUDE_작업진행서_20260115_0933.md
- WORK_SUMMARY_20260114_AFTERNOON.md
- README_AFTERNOON.md
- JNEXT_SUMMARY_20260115.md

**구조**:
```markdown
# JNext 작업 이력

**목적**: 날짜별 작업 내역 통합 기록

---

## 2026-01-15

### 오전 작업 (06:53 - 09:33)
**목표**: 전자책 출판 준비

**완성**:
- 전자책 폰트 (Noto Serif/Sans KR)
- DALL-E 3 이미지 생성
- Firebase Storage 연동
- 반응형 이미지 레이아웃

**파일**:
- api/templates/document_manager.html
- api/api/views_v2.py
- api/config/urls.py

---

## 2026-01-14

### 오후 작업
**목표**: JNext v2 핵심 시스템 구축

**완성**:
- 듀얼 슬라이더 (Temperature + DB Focus)
- 3-Stage Storage (RAW 자동 저장)
- Hierarchical Firestore (projects/{project_id}/)
- AI 자기언급 제거

**파일**:
- 11개 파일 수정
- 70개 문서 마이그레이션

---

## 2026-01-12

### 호버 효과 수정
- hino_review.html CSS 최적화
- 카드 크기 변화 제거
```

---

#### 1-2. CLAUDE_GUIDE.md 개선
**기존**: CLAUDE_GUIDE.md  
**추가**: 최신 가이드라인 통합

**구조**:
```markdown
# JNext 프로젝트 가이드 for Claude

## 1. 기본 원칙
- J님을 항상 "J님"으로 호칭
- 존댓말 사용

## 2. 프로젝트 구조
- JNext = 플랫폼
- 하이노밸런스 = 프로젝트

## 3. 일반적인 문제 해결
- API 수정 반영 안됨 → 프로세스 완전 종료
- URL 라우팅 추적
- AI SDK 충돌

## 4. 세션 복구 방법
- README.md 먼저 읽기
- JNEXT_CORE_VISION.md 확인
- CLAUDE_인수인계_*.md 최신 파일 확인
```

---

### Phase 2: 삭제 작업

**삭제 대상 (12개)**:
```
❌ STRUCTURE_20260114.md
❌ STRUCTURE_20260114_2150.md
❌ CLAUDE_작업진행서_20260115_0933.md (통합 후)
❌ WORK_SUMMARY_20260114_AFTERNOON.md (통합 후)
❌ README_AFTERNOON.md (통합 후)
❌ JNEXT_SUMMARY_20260115.md (통합 후)
❌ GEMINI_API_ISSUE.md
❌ 작업정리_hino_review_hover_fix.md
❌ Gin_2026015_advice.md
❌ CURRENT_STATUS.md
❌ JNEXT_V2_IMPLEMENTATION_PLAN.md
❌ CLAUDE_GUIDE.md (개선 버전으로 대체)
```

---

### Phase 3: 폴더 구조 정리

**새 구조**:
```
docs/
├── 00_CORE/                        # 핵심 비전 & 가이드
│   ├── JNEXT_CORE_VISION.md       ⭐ J님 비전
│   ├── ARCHITECTURE_PRINCIPLES.md  PaaS 구조
│   ├── JNEXT_VS_HINOBALANCE.md    플랫폼 vs 프로젝트
│   └── CLAUDE_GUIDE.md            Claude 작업 가이드
│
├── 01_DESIGN/                      # 설계 & 구조
│   ├── DESIGN_DOCUMENT.md         전체 설계서
│   ├── STRUCTURE.md               최신 구조
│   └── AI_MODEL_STRATEGY.md       AI 모델 전략
│
├── 02_ROADMAP/                     # 개발 계획
│   ├── JNEXT_ROADMAP.md           8단계 파이프라인
│   ├── CODE_REFACTORING_PLAN_20260115.md
│   └── DAILY_PLAN_20260115.md
│
├── 03_CONTENT/                     # 콘텐츠 자동화
│   ├── IMAGE_AND_EBOOK_PLAN.md
│   ├── FINAL_SCHEMA.md
│   ├── MEME_PRODUCTION_GUIDE.md
│   └── HINO_CATEGORY_STRUCTURE.md
│
├── 04_HANDOVER/                    # Claude 인수인계
│   ├── CLAUDE_인수인계_20260115_0940.md ⭐ 최신
│   └── WORK_HISTORY.md            🆕 작업 이력 통합
│
├── 05_CONVERSATIONS/               # 대화 기록
│   ├── conversation_001.md
│   └── conversation_002_jbody_analysis.md
│
├── 06_LEGACY/                      # 참고용 (과거 문서)
│   ├── CODE_STRUCTURE_ANALYSIS_20260110.md
│   └── IMPROVEMENT_PLAN.md
│
└── 07_OPERATIONS/                  # 운영
    ├── TESTING_CHECKLIST.md
    ├── SECURITY_SCHEDULE.md
    └── JNext.code-workspace
```

---

## 🎯 정리 효과

### Before (33개)
- 중복 문서 많음
- 구조 없이 나열
- 찾기 어려움

### After (21개 + 7개 폴더)
- **핵심 문서 명확**
- **폴더별 분류**
- **빠른 검색**

**감소**: 33개 → 21개 (36% 감소)

---

## ⚠️ 주의사항

### 백업 먼저!
```powershell
# 전체 docs 폴더 백업
Copy-Item -Path "C:\Projects\JNext\docs" -Destination "C:\Projects\JNext\docs_backup_20260115" -Recurse
```

### Git 커밋
```powershell
git add docs/
git commit -m "docs: 문서 정리 및 구조화 (33→21개)"
git push
```

### 롤백 가능
- 백업 폴더 보관
- Git 히스토리 유지

---

## 📅 실행 순서

1. **백업 생성** (5분)
2. **Phase 1: 통합** (20분)
   - WORK_HISTORY.md 생성
   - CLAUDE_GUIDE.md 개선
3. **Phase 2: 삭제** (5분)
   - 12개 파일 삭제
4. **Phase 3: 폴더 구조** (10분)
   - 7개 폴더 생성
   - 파일 이동
5. **검증** (10분)
   - 링크 확인
   - 누락 없는지 체크
6. **Git 커밋** (5분)

**총 소요 시간**: 약 1시간

---

## 💬 J님께 확인 사항

1. **폴더 구조**: 7개 폴더로 분류하는 것 괜찮으신가요?
   - 00_CORE, 01_DESIGN, 02_ROADMAP...
   - 아니면 flat 구조 유지?

2. **삭제 대상**: 12개 파일 삭제 동의하시나요?
   - 특히 GEMINI_API_ISSUE.md, Gin_2026015_advice.md

3. **대화 기록**: conversation_*.md 2개는 보관?
   - 아니면 삭제?

4. **실행 시점**: 지금 바로? 아니면 내일?

**제 추천**: 
- ✅ 폴더 구조 괜찮음 (검색 편리)
- ✅ 12개 삭제 OK (백업 있음)
- ✅ 대화 기록 보관 (중요 맥락)
- ✅ **지금 바로 실행** (30분이면 끝)

승인하시면 바로 시작하겠습니다, J님! 🚀
