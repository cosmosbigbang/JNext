# JNext v2 구조 분석 (2026-01-14)

**작성일**: 2026-01-14  
**작성자**: J님 + Claude  
**목적**: 오늘(2026-01-14) 작업 내용 구조화 및 마이그레이션 준비  

---

## 📋 오늘 작업 요약

### Phase 1: 슬라이더 2개 분리 ✅
**목적**: Temperature와 DB 사용률을 독립적으로 조절

**변경된 파일**:
1. `backend/templates/chat_v2.html` (922줄 → 960줄)
   - 슬라이더 1개 → 2개로 분리
   - Temperature 슬라이더: 0-100 (UI) → 0.0-1.0 (실제값), 기본 85 (0.85)
   - DB 사용률 슬라이더: 0-100%, 기본 25% (대화), 50% (프로젝트)
   - JavaScript 이벤트 핸들러 추가

2. `backend/api/views_v2.py` (239줄 → 242줄)
   - 파라미터 추가: `temperature`, `db_focus`
   - 기존 `focus` 제거
   - ContextManager 호출 시 새 파라미터 전달

3. `backend/api/core/context_manager.py` (219줄 → 228줄)
   - `build_context()` 시그니처 변경
   - 파라미터: `focus` → `temperature`, `db_focus`
   - 자동 계산 제거, 슬라이더 값 직접 사용

**핵심 로직**:
```python
# UI (JavaScript)
temperature = parseFloat((tempSlider.value / 100).toFixed(2))  // 0.85
db_focus = parseInt(dbSlider.value)  // 25 or 50

# API (views_v2.py)
temperature = float(data.get('temperature', 0.85))
db_focus = int(data.get('db_focus', 25))

# ContextManager
context = ContextManager.build_context(
    temperature=temperature,  # 직접 사용
    db_focus=db_focus,        # 가중치 계산에만 사용
    ...
)
```

---

### Phase 2: 데이터 구조 재설계 ✅
**목적**: chat_history 필드 확장 및 RAW 저장 준비

**변경된 파일**:
1. `backend/api/views.py` (2383줄 → 2383줄)
   - `save_chat_history()` 함수 확장
   - 새 파라미터: `temperature`, `db_focus`, `project_context`
   - 반환값: `doc_id` (RAW 저장 시 참조용)

**확장된 Firestore 스키마**:
```python
# 기존
chat_history/{timestamp_id}:
  - 역할: "user" | "assistant"
  - 내용: "..."
  - 시간: timestamp
  - 모드: "v2"
  - 모델: "gemini-pro"

# 신규 (Phase 2)
chat_history/{timestamp_id}:
  - 역할: "user" | "assistant"
  - 내용: "..."
  - 시간: timestamp
  - 모드: "v2"
  - 모델: "gemini-pro"
  + temperature: 0.85          # 새로 추가
  + db_focus: 25               # 새로 추가
  + project_context: "hinobalance" | null  # 새로 추가
  + raw_분석_완료: false | true  # 새로 추가
  + raw_저장_위치: "hinobalance_raw/xxx"  # 조건부
```

---

### Phase 3: 3단계 저장 프로세스 ✅
**목적**: 프로젝트 대화 자동 분석 및 RAW 저장

**새로 추가된 파일**:
1. `backend/api/raw_storage.py` (신규, 146줄)
   - `evaluate_chat_value()`: AI 가치 평가 (관대한 필터링)
   - `analyze_and_save_raw()`: AI 분석 후 RAW 저장

**변경된 파일**:
1. `backend/api/views_v2.py`
   - Phase 3 로직 추가 (6번 응답 처리 부분)
   - 프로젝트 대화 → 평가 → 분석 → RAW 저장

**3단계 프로세스 흐름**:
```
사용자 메시지 입력
  ↓
[Stage 1] chat_history 즉시 저장 (백업)
  - save_chat_history() 호출
  - doc_id 반환
  ↓
AI 대화 처리 (기존 로직)
  ↓
AI 응답 저장
  ↓
if project_id exists:  # 프로젝트 대화만
  ↓
[Stage 2] 가치 평가
  - evaluate_chat_value() 호출
  - AI에게 물어봄 (temp 0.2, gemini-flash)
  - 관대한 판단 (애매하면 yes)
  ↓
if is_valuable:  # 가치 있는 대화만
  ↓
[Stage 3] AI 분석 + RAW 저장
  - analyze_and_save_raw() 호출
  - AI가 제목, 키워드, 카테고리, 요약 추출 (temp 0.3)
  - {project_id}_raw 컬렉션에 저장
  - chat_history 업데이트 (raw_분석_완료=true)
```

**RAW 컬렉션 스키마**:
```python
{project_id}_raw/{timestamp_id}:
  - id: "20260114_093000_123456"
  - 제목: "하이노워킹 크로스 개선안"  # AI 생성
  - 원본: "사용자 원본 메시지"
  - ai_응답: "AI 답변 원본"
  - 정리본: "AI가 요약/정제한 내용"
  - 키워드: ["하이노워킹", "크로스", "골반"]  # AI 추출
  - 카테고리: "하이노워킹"  # AI 분류
  - 태그: []
  - 요약: "50자 핵심 요약"  # AI 생성
  - chat_ref: "20260114_093000_123456"  # 원본 대화 ID
  - project_id: "hinobalance"
  - 시간: timestamp
  - 작성자: "J님"
  - 모델: "gemini-pro"
```

---

## 🚨 발견된 문제점

### 1. 컬렉션 네이밍 불일치
**문제**:
- 기존 컬렉션: `hino_raw`, `hino_draft`, `hino_final`, `hino_theory`
- project_id: `"hinobalance"`
- 새 코드: `{project_id}_raw` → `hinobalance_raw`
- 결과: **새로운 컬렉션 생성됨** (기존 데이터와 분리!)

**원인**:
- 초기 하드코딩: 컬렉션을 `hino_*`로 생성
- project_id와 불일치: `hinobalance` vs `hino`
- JNext 범용화 미흡

**해결 필요**:
- 마이그레이션: `hino_*` → `hinobalance_*`
- 일관성 확보

### 2. 파일 구조 (현재)
```
backend/api/
├── views.py                    # 2383줄 (기존 레거시)
├── views_v2.py                 # 242줄 (v2 채팅 API)
├── core/
│   └── context_manager.py      # 228줄 (동적 맥락 관리)
├── projects/
│   └── project_manager.py      # (프로젝트 관리, 기존)
├── ai_service.py               # 431줄 (AI 호출)
├── raw_storage.py              # 146줄 (Phase 3, 신규)
├── db_service.py               # (DB 접근)
└── meme_generator.py           # (밈 생성)

backend/templates/
└── chat_v2.html                # 960줄 (슬라이더 2개)
```

---

## 📊 Firestore 구조 (현재)

### 기존 컬렉션 (마이그레이션 대상)
```
hino_raw/              # 하이노밸런스 RAW (기존)
hino_draft/            # 하이노밸런스 DRAFT (기존)
hino_final/            # 하이노밸런스 FINAL (기존)
hino_theory/           # 하이노밸런스 이론 (기존)
chat_history/          # 전체 대화 백업 (확장됨)
```

### 오늘 작업 후 생성된 컬렉션
```
hinobalance_raw/       # ⚠️ 새로 생성됨 (잘못된 네이밍)
```

### 목표 구조 (마이그레이션 후)
```
chat_history/          # 전체 대화 백업 (확장 완료 ✅)

hinobalance_raw/       # 하이노밸런스 RAW
hinobalance_draft/     # 하이노밸런스 DRAFT
hinobalance_final/     # 하이노밸런스 FINAL
hinobalance_theory/    # 하이노밸런스 이론

jbody_raw/             # JBody RAW (미래)
jbody_draft/           # JBody DRAFT (미래)
jbody_final/           # JBody FINAL (미래)

projects_meta/         # 프로젝트 메타 정보 (Phase 4)
```

---

## 🎯 다음 작업 계획

### 즉시 필요: 마이그레이션
**목적**: 컬렉션 네이밍 일관성 확보

**작업 내용**:
1. `hino_raw` → `hinobalance_raw` 복사
2. `hino_draft` → `hinobalance_draft` 복사
3. `hino_final` → `hinobalance_final` 복사
4. `hino_theory` → `hinobalance_theory` 복사
5. 기존 `hino_*` 삭제 (백업 후)
6. `project_manager.py` 수정
7. 검증

**예상 시간**: 10-15분

### Phase 4: 프로젝트 동적 생성 (보류)
**목적**: 대화 중 신규 프로젝트 자동 생성

**작업 내용**:
- `projects_meta` 컬렉션 설계
- `create_project()` 함수
- `/api/v2/projects` 엔드포인트
- UI 동적 드롭다운

### Phase 5: AI 자기언급 제거 (보류)
**목적**: DRAFT/FINAL 생성 시 순수한 지식만

**작업 내용**:
- 프롬프트 강화
- 정규식 후처리
- 기존 데이터 정리

---

## 📈 진행 상황

### 완료 ✅
- [x] Phase 1: 슬라이더 2개 분리
- [x] Phase 2: 데이터 구조 재설계
- [x] Phase 3: 3단계 저장 프로세스

### 진행 중 🔄
- [ ] 컬렉션 마이그레이션 (hino_* → hinobalance_*)

### 대기 ⏸️
- [ ] Phase 4: 프로젝트 동적 생성
- [ ] Phase 5: AI 자기언급 제거
- [ ] Phase 6: 테스트 & 최적화

---

## 🔍 핵심 개선 사항

### 1. 슬라이더 독립성
**변경 전**:
- 슬라이더 1개 (focus 0-100)
- Temperature 자동 계산 (0.7 - focus*0.5)
- DB 가중치 자동 계산

**변경 후**:
- 슬라이더 2개 (독립적)
- Temperature: J님이 직접 조절 (0.0-1.0)
- DB 사용률: J님이 직접 조절 (0-100%)
- 최적값 탐색 가능

### 2. 데이터 추적성
**변경 전**:
- chat_history만 저장
- 프로젝트 컬렉션 수동 저장

**변경 후**:
- chat_history: 전체 백업 (확장 필드)
- 자동 평가 → RAW 저장
- 출처 추적: FINAL → DRAFT → RAW → chat_history

### 3. 자동화
**변경 전**:
- 수동 저장
- 수동 분류

**변경 후**:
- 자동 가치 평가
- AI 자동 분석 (제목, 키워드, 카테고리)
- 자동 RAW 저장

---

## 💡 J님 피드백 반영

### 1. 슬라이더 우선순위
> "슬라이더는 우선해야해.. 자동 조절되지만.. 슬라이더 통제는 내가 직접하므로 가장 안전함"

✅ 구현: 슬라이더 2개로 분리, J님이 직접 통제

### 2. RAW/DRAFT/FINAL 정의
> "raw, draft, final은 저장단계에서 필요한거야.. 기본 raw이고.. draft 만들려면 검색해서 문서 가지고 오고 정리해서 마음에 들면 draft로 저장해"

✅ 이해: 저장 컬렉션 구분, 작업 단계 아님

### 3. AI 자기언급 제거
> "draft저장시 젠, 진,클로 등등 ai 애기는 모두 제거해야해"

✅ 계획: Phase 5에서 구현 예정

### 4. 1차 필터링 관대함
> "순수한 잡담이지.. 내용 통제를 심하게 하면 왜곡이 발생 우려됨"

✅ 구현: evaluate_chat_value()에서 관대한 필터링

### 5. 컬렉션 일관성
> "어차피 JNext프로젝트에 많은 프로젝트(컬렉션) 생기므로 마이그레이션으로 제대로 해"

✅ 다음: 마이그레이션 진행 예정

---

## 📝 남은 이슈

### 1. 마이그레이션 (최우선)
- hino_* → hinobalance_*
- 데이터 무결성 검증

### 2. 테스트 부족
- 슬라이더 2개 동작 확인 필요
- 3단계 저장 프로세스 검증 필요
- RAW 저장 품질 확인 필요

### 3. 문서화
- API 문서 업데이트
- 사용자 가이드 작성

---

**다음 단계**: 컬렉션 마이그레이션 스크립트 작성 및 실행
