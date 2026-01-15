# JNext 작업 이력

**목적**: 날짜별 주요 작업 내역 통합 기록  
**관리**: Claude 세션별 작업 내용 누적

---

## 2026-01-15 (수요일)

### 오전 작업 (06:53 - 09:33, 2시간 40분)
**담당**: Claude (클로) + J님  
**목표**: 전자책 출판 준비 시스템 구축

#### ✅ 완성 항목

**1. 전자책 출판용 폰트 시스템**
- 본문: Noto Serif KR (16px, 줄간격 2.0)
- 제목: Noto Sans KR (18-24px, 굵게)
- 여백: 좌우 40px
- word-break: keep-all

**2. AI 이미지 생성 시스템 (DALL-E 3)**
- 9가지 크기 옵션 (1024/512/256 × 정사각/가로/세로)
- 프롬프트 입력 + 스타일 선택
- Firebase Storage 자동 업로드
- 문서 삽입 원클릭
- 비용: $0.04/장

**3. Firebase Storage 연동**
- 버킷: jnext-e3dd9.firebasestorage.app
- 공개 URL 자동 생성
- Firestore 메타데이터 저장

**4. 반응형 이미지 레이아웃**
- 대형(1024px): 중앙 정렬, display: block
- 중형(512px): float left, margin-right
- 소형(256px): float right, margin-left
- 마크다운 자동 변환

**5. 캐릭터 스타일 분석 (Gemini Vision)**
- 기존 이미지 스타일 분석
- 메모리 캐싱 (최초 1회만)
- 비용 절감

#### 📁 변경 파일
- `api/templates/document_manager.html`
- `api/api/views_v2.py` (generate_image() 추가)
- `api/config/urls.py`
- `api/requirements.txt` (openai, pillow 추가)

#### 💾 Git 상태
- Commit: a459af3
- Push 완료
- 서버: 실행 중

#### 📌 보류 작업
- 밈 이미지 자동 생성 (DALL-E 캐릭터 일관성 한계)
- 대안: meme_images/ 폴더 기존 이미지 재사용

---

### 오후 작업 (15:00 - 진행 중)
**담당**: Claude (클로) + J님  
**목표**: 코드 리팩터링 계획 + docs 정리

#### ✅ 완성 항목

**1. 전체 코드 분석**
- views.py: 2,305줄 (비대)
- views_v2.py: 1,268줄 (큼)
- 총 3,573줄 → 1,650줄로 감소 목표 (54%)

**2. 리팩터링 계획 수립**
- 3단계 아키텍처 (View → Service → Repository)
- 8개 Phase (준비 → Repository → Service → View → URL → 하이노 제거 → 테스트 → 레거시 삭제)
- 예상 시간: 13시간 (2일)

**3. docs 폴더 정리 계획**
- 33개 → 21개 파일 (36% 감소)
- 7개 폴더 구조 (CORE/DESIGN/ROADMAP/CONTENT/HANDOVER/CONVERSATIONS/LEGACY/OPERATIONS)
- 중복 문서 통합, 해결된 이슈 삭제

#### 📁 생성 파일
- `CODE_REFACTORING_PLAN_20260115.md` (리팩터링 계획서)
- `DOCS_CLEANUP_PLAN_20260115.md` (문서 정리 계획)
- `WORK_HISTORY.md` (이 파일)

#### 🔄 진행 중
- docs 폴더 정리 실행

---

## 2026-01-14 (화요일)

### 오후 작업
**목표**: JNext v2 핵심 시스템 구축

#### ✅ 완성 항목

**1. 듀얼 슬라이더 시스템**
- Temperature: 0-100 (UI) → 0.0-1.0 (실제)
- DB Focus: 0-100%
- 프로젝트 선택 시 DB 자동 전환 (25% ↔ 50%)

**2. chat_history 스키마 확장**
- 5개 필드 추가:
  - temperature (float)
  - db_focus (int)
  - project_context (str)
  - raw_분석_완료 (bool)
  - raw_저장_위치 (str)

**3. 3-Stage Storage 프로세스**
```
사용자 메시지 → AI 응답
  ↓
chat_history 저장 (백업)
  ↓
evaluate_chat_value() - AI 평가 (temp 0.2)
  ↓
analyze_and_save_raw() - AI 분석 (temp 0.3)
  ↓
projects/{project_id}/raw/{timestamp} 저장
```

**4. AI 자기언급 제거**
- 프롬프트 강화
- Regex 후처리 ("제가", "저는", "젠", "클로" 등)

**5. Hierarchical Firestore**
- 구조 변경: `hino_raw/` → `projects/hinobalance/raw/`
- 70개 문서 마이그레이션 (raw 39개 + draft 31개)

**6. DynamicProject System Prompt 간소화**
- 3,500자 → 600자 (80% 감소)
- 핵심만 남김

**7. docs 폴더 자동 검색**
- DB 없는 신규 프로젝트도 기획 문서 자동 참고

#### 📁 변경 파일 (11개)
- `chat_v2.html`
- `views_v2.py`
- `context_manager.py`
- `views.py`
- `raw_storage.py` (신규)
- `hinobalance.py`
- `project_manager.py`
- `ai_service.py`
- `automation.py`
- `settings.py`
- `base.py`

#### 📁 생성 파일
- `test_v2_complete.py` (6개 자동 테스트)
- `WORK_SUMMARY_20260114_AFTERNOON.md`
- `TESTING_CHECKLIST.md`

#### 🗄️ 데이터
- 70개 문서 마이그레이션
- projects/hinobalance 메타데이터 생성
- 구형 컬렉션 보존 (롤백 대비)

---

## 2026-01-12 (일요일)

### hino_review.html 호버 효과 수정
**목표**: 카드 호버 시 크기 변화 제거

#### ✅ 완성 항목
- CSS transform/box-shadow 제거
- 투명도/색상만 변경
- Draft 탭 정상 작동 확인

#### ⚠️ 문제
- Contents/Raw 탭 여전히 이슈
- JavaScript 스타일 오버라이드 의심

#### 📁 변경 파일
- `backend/templates/hino_review.html`
- 백업: `hino_review_backup_v3.0_FINAL_20260112.html`

---

## 2026-01-10 (금요일)

### 코드 구조 분석
**목표**: 전체 아키텍처 현황 파악

#### ✅ 완성 항목
- Intent 분류 시스템 분석
- Temperature 기반 통제 검토
- 명명 규칙 일관성 체크

#### 📁 생성 파일
- `CODE_STRUCTURE_ANALYSIS_20260110.md`

---

## 2026-01-09 (목요일)

### AI 모델 전략 수립
**목표**: 프로젝트별 AI 모델 구분

#### ✅ 완성 항목
- 하이노밸런스: Gemini Pro (주력) + GPT-4o (보조)
- 모의고사앱: Gemini Flash (빠른 응답, 비용 효율)
- 모드별 자동 선택 로직

#### 📁 생성 파일
- `AI_MODEL_STRATEGY.md`

---

## 작업 패턴 분석

### Temperature 설정
```
RAW (대화):    0.7-0.85  (창의 최고)
DRAFT (정리):  0.5-0.55  (균형)
FINAL (확정):  0.2-0.3   (정확)
밈/숏 생성:    0.6-0.7   (창의)
전자책:        0.2-0.3   (정확)
```

### DB Focus 설정
```
대화 모드:     25%  (일반 지식 중심)
프로젝트 모드: 50%  (균형)
전문 분석:     70-85% (DB 전문가)
```

### 가중치 계산
```
대화 맥락: 15% (고정)
프로젝트 DB: 15 + (db_focus × 0.7) = 15-85%
일반 지식: 나머지
```

---

**다음 작업 예정**:
- 내일 (1/16): 코드 리팩터링 Phase 1-3
- 주말: 콘텐츠 자동화 파이프라인 구축
