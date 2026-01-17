# JNext 전체 시스템 분석 보고서

**작성일**: 2026-01-17  
**작성자**: Claude (클로)  
**목적**: JNext 프로젝트 전체 파악 및 업무 이해

---

## 📊 프로젝트 개요

### 핵심 미션
**J님의 창의성을 손실 없이 저장하고, AI 증폭을 통해 최종 상품으로 자동 변환**

- **1차 목표**: 아이디어 저장 및 보존
- **2차 목표**: 자동 상품화 (앱/웹/전자책/밈/숏폼)

### 아키텍처 개념
```
JNext (플랫폼)
├── Backend: Django + Firebase Firestore
├── AI Layer: Gemini Pro/Flash, GPT-4o, Claude
├── Projects: 프로젝트별 플러그인 구조
│   └── HinoBalance (첫 번째 프로젝트)
└── Mobile Apps: Flutter (hinobalance_mobile, jnext_mobile)
```

---

## 🔧 기술 스택

### Backend
- **Framework**: Django 6.0
- **Database**: Firebase Firestore (NoSQL)
- **Local DB**: SQLite (chat_history 저장)
- **Python**: 3.14

### AI Models
- **Gemini**: Pro (정확성), Flash (속도)
- **GPT**: 4o (창의성)
- **Claude**: Sonnet (균형)
- **별명**: 젠(Gemini Pro), 젠시(Flash), 진(GPT), 클로(Claude)

### Mobile
- **Framework**: Flutter
- **Apps**: hinobalance_mobile (특화), jnext_mobile (범용)

### Infrastructure
- **Deployment**: Render.com (render.yaml)
- **Static Files**: Whitenoise
- **Environment**: .env, service account key

---

## 📂 파일 구조 분석

### api/ (Django Backend)
```
api/
├── api/                          # Django 앱
│   ├── ai_config.py             # AI 설정 중앙 관리 ⭐
│   ├── ai_service.py            # AI 모델 호출 (멀티모델 추상화)
│   ├── views.py                 # 기본 API
│   ├── views_v2.py              # v2 채팅 API (정밀분석, 세션학습)
│   ├── session_learning.py      # 세션 간 학습 관리 ⭐
│   ├── db_service.py            # Firestore 통합 서비스
│   ├── raw_storage.py           # RAW 데이터 저장 및 분석
│   ├── meme_generator.py        # 밈 생성
│   ├── automation.py            # 자동화 스크립트
│   ├── core/
│   │   └── context_manager.py  # 동적 맥락 관리 (슬라이더 기반)
│   └── projects/
│       ├── project_manager.py   # 프로젝트 관리 싱글톤
│       ├── base.py              # BaseProject 추상 클래스
│       └── hinobalance.py       # HinoBalance 프로젝트 설정
│
├── config/                      # Django 설정
│   ├── settings.py              # 환경 설정 (Firebase, AI, DB)
│   └── urls.py                  # URL 라우팅
│
├── scripts/                     # 범용 유틸리티 (40개)
│   ├── check/                   # DB 상태 확인 (13개)
│   ├── test/                    # API 테스트 (7개)
│   └── utils/                   # 기타 도구 (20개)
│
├── templates/                   # HTML 템플릿
│   └── chat_v2.html             # v2 채팅 UI
│
└── manage.py                    # Django CLI
```

### projects/ (프로젝트별 데이터)
```
projects/
└── hinobalance/
    ├── data/                    # 원본 데이터
    │   ├── theory/              # 이론 카테고리
    │   ├── exercises/           # 운동 개별
    │   └── combined/            # 통합 문서
    ├── scripts/                 # 전용 스크립트
    │   ├── upload/              # 업로드 스크립트
    │   ├── organize/            # 정리 스크립트
    │   ├── publishing.py        # Draft → Final 변환
    │   └── analyze.py           # 분석 도구
    └── docs/                    # 프로젝트 문서
```

### docs/ (전체 문서)
```
docs/
├── 00_CORE/                     # 핵심 비전 및 아키텍처
│   ├── JNEXT_CORE_VISION.md
│   ├── PROJECT_STRUCTURE.md
│   ├── JNEXT_VS_HINOBALANCE.md
│   └── AI_ONBOARDING/           # AI 프롬프트 (이동됨)
│       ├── PROMPT_클로.md
│       ├── PROMPT_젠.md
│       └── prompt_진.md
│
├── 01_DESIGN/                   # 설계 문서
│   ├── DESIGN_DOCUMENT.md
│   ├── AI_MODEL_STRATEGY.md
│   └── ARCHITECTURE_ANALYSIS_20260116.md
│
├── 02_ROADMAP/                  # 로드맵
│   └── JNEXT_ROADMAP.md
│
├── 03_CONTENT/                  # 콘텐츠 스키마
│   ├── FINAL_SCHEMA.md
│   └── HINO_CATEGORY_STRUCTURE.md
│
├── 04_HANDOVER/                 # 인수인계
│   ├── CLAUDE_인수인계_20260116_1730.md (최신)
│   └── WORK_HISTORY.md
│
├── 05_CONVERSATIONS/            # 대화 기록 (이동됨)
│   ├── 품질저하_진_01~03.md
│   ├── 품질저하_젠_01~02.md
│   └── gemini_advice_*.md
│
├── 06_LEGACY/                   # 레거시
├── 07_OPERATIONS/               # 운영
│
├── 구조변경_2026-01-16.md       # 리팩터링 기록
└── 작업일정.md                  # 현재 작업 계획
```

---

## 🔄 데이터 플로우

### 3단계 AI 증폭 파이프라인
```
RAW (1차 증폭)
├─ 입력: J님의 원본 아이디어/대화
├─ AI 처리: 초기 구조화 + 분석
├─ 저장: projects/{project_id}/raw/{doc_id}
└─ 자동화: AI가 대화 분석 → 컬렉션 선택

    ↓

DRAFT (2차 증폭)
├─ 입력: 복수의 RAW 데이터
├─ AI 처리: 총론 + 각론 정리
├─ 저장: projects/{project_id}/draft/{doc_id}
└─ 자동화: 카테고리 확정 (→ 앱/웹 메뉴)

    ↓

FINAL (최종 확정)
├─ 입력: DRAFT 최종본
├─ AI 처리: 출판용 문장 리듬 조정
├─ 저장: projects/{project_id}/final/{doc_id}
└─ 자동화: 앱/웹/전자책/밈/숏폼 자동 생성

    ↓

상품 출시
├─ 앱: Flutter 자동 생성 (카테고리 = 메뉴)
├─ 웹: 웹사이트 자동 생성
├─ 전자책: e-book 자동 생성
├─ 밈: 밈 이미지 자동 생성
└─ 숏: 숏폼 영상 자동 생성
```

### Firestore 구조
```
Firestore
├── projects/
│   └── {project_id}/           # 프로젝트별 격리
│       ├── raw/                # 원본 + 1차 증폭
│       ├── draft/              # 2차 증폭
│       └── final/              # 최종 확정
│
├── chat_history/               # 대화 기록 (SQLite로 이동 예정)
├── session_learning/           # 세션 학습 내용 ⭐ NEW
└── system_logs/                # 시스템 로그
```

---

## 🤖 AI 시스템 설계

### 1. 중앙 관리: ai_config.py
```python
# 모델 별명
MODEL_ALIASES = {
    'gemini-pro': '젠',
    'gpt': '진',
    'claude': '클로'
}

# Temperature 설정
TEMPERATURE_SETTINGS = {
    'organize': 0.3,    # 사실 중심
    'hybrid': 0.5,      # 균형
    'analysis': 0.7,    # 창의성
    'v2': 0.5           # v2 기본값
}

# 동적 프롬프트 생성
def get_hinobalance_prompt(project_id='hinobalance'):
    # 최근 세션 학습 내용 로드
    recent_learning = load_recent_learning(project_id, limit=3)
    return base_prompt + learning_section + ...
```

### 2. AI 서비스: ai_service.py
- **멀티모델 추상화**: Gemini, GPT, Claude 통합
- **Native History**: 각 모델에 메시지 리스트 직접 전달
- **Intent Classification**: 사용자 의도 감지 (SAVE/READ/UPDATE/DELETE/ORGANIZE)
- **Response Validation**: JSON 스키마 검증

### 3. 세션 학습: session_learning.py ⭐
```python
# 자동 학습 (10개 대화마다)
auto_summarize_learning(conversation_history, model, project_id)

# 학습 로드 (최근 3개)
load_recent_learning(project_id, limit=3)

# 학습 저장
save_session_learning(project_id, model, learning_summary)
```

### 4. 동적 맥락: context_manager.py
```python
# 슬라이더 2개로 맥락 조절
build_context(
    temperature,      # 창의성 (0.0-1.0)
    db_focus,        # DB 사용률 (0-100)
    project_id,
    user_message,
    conversation_history
)

# DB OFF (focus=0): 대화 100%
# DB ON (focus=100): 대화 30% + DB 70%
```

---

## 🎯 핵심 기능

### 1. "정밀분석해" 특수 명령어
- **목적**: 7개 항목 구조화 분석 생성
- **형식 강제**: 마크다운 (JSON 절대 금지)
- **항목**:
  1. 본질 분석
  2. 효과
  3. 대상
  4. 동작 요약
  5. 평점
  6. 장단점
  7. 개선점

### 2. 세션 학습 시스템
- **자동 학습**: 대화 10개마다 자동 요약 저장
- **수동 학습**: "학습정리" 명령어로 즉시 요약
- **학습 반영**: "정밀분석해" 시 최근 3개 학습 내용 적용
- **목적**: AI가 J님의 선호도와 피드백을 세션 간 보존

### 3. Native History 패턴
- Gemini: `contents` 파라미터에 메시지 리스트 전달
- GPT: `messages` 파라미터에 메시지 리스트 전달
- Claude: `messages` 파라미터에 메시지 리스트 전달
- **효과**: 컨텍스트 관리 최적화, 일관성 향상

### 4. 프로젝트 시스템
- **플러그인 구조**: BaseProject 상속으로 새 프로젝트 추가
- **카테고리 = 메뉴**: 카테고리 분류가 앱/웹 메뉴로 자동 변환
- **DB 격리**: 프로젝트별 독립적인 Firestore 경로

### 5. 품질 관리
- **자동 품질 평가**: RAW 저장 시 품질 점수 자동 계산
- **키워드 감지**: J님 키워드 누락, 일반론 감지
- **검증 플래그**: 검증 필요 문서 자동 표시

---

## 📱 HinoBalance 프로젝트 (첫 번째 테스트 케이스)

### 정의
**가속도 제어와 한발 불안정성으로 신경-근육을 통합 훈련하는 시스템**

### 핵심 철학
1. **한발 철학**: 두발=정지=균형=죽음 / 한발=출발=불균형=삶
2. **가속도 자극**: F=ma, Δt→0 = 무한대 부하
3. **신경 우선**: 근육보다 신경 먼저 → 근력은 부산물

### 카테고리 구조
```
이론
├── 요약
├── 중간
├── 전체
└── 가치

실전
├── 하이노워밍
├── 하이노골반
├── 하이노워킹
├── 하이노스케이팅
├── 하이노풋삽
└── 하이노철봉

밈
숏
```

### AI 프롬프트 전략
- **클로**: 신체 내부 연결·전달·상태 변화 관점
- **젠**: 정확한 분석, 구조화
- **진**: 창의적 표현, 철학적 깊이

---

## 🚀 현재 작업 상태 (2026-01-17)

### ✅ 완료된 작업
- [x] 폴더 기반 구조 리팩터링 (projects/hinobalance/)
- [x] 세션 학습 시스템 구현
- [x] "정밀분석해" 특수 명령어
- [x] Native History 패턴 완성
- [x] Circular Import 해결
- [x] docs 폴더 정리 (8개 섹션 구조)
- [x] README.md 업데이트 (최신 기능 반영)

### 🔄 진행 중
- **Phase 1**: 신규 운동 2~3개 등록 및 테스트
  - "정밀분석해" 기능 활용
  - 품질 검증 및 피드백
  - 진, 젠의 학습 패턴 관찰

### 📋 예정
- **Phase 2**: 전체 이론/운동 정리 (draft → final)
- **Phase 3**: 전자책 출판 준비

---

## 🔑 핵심 파일 위치

### AI 설정
- `api/api/ai_config.py` - 모델 별명, Temperature, 시스템 프롬프트
- `api/api/ai_service.py` - 멀티모델 호출, Intent 분류
- `api/api/session_learning.py` - 세션 학습 관리

### API
- `api/api/views_v2.py` - v2 채팅 API (정밀분석, 학습정리)
- `api/api/views.py` - 기본 API
- `api/config/urls.py` - URL 라우팅

### DB
- `api/api/db_service.py` - Firestore 통합 서비스
- `api/api/raw_storage.py` - RAW 저장 및 분석
- `api/config/settings.py` - Firebase 초기화

### 프로젝트
- `api/api/projects/project_manager.py` - 프로젝트 관리
- `api/api/projects/hinobalance.py` - HinoBalance 설정
- `api/api/core/context_manager.py` - 동적 맥락 관리

### 스크립트
- `projects/hinobalance/scripts/publishing.py` - Draft → Final 변환
- `projects/hinobalance/scripts/upload/` - 업로드 스크립트
- `api/scripts/check/` - DB 상태 확인 도구

### 문서
- `docs/00_CORE/JNEXT_CORE_VISION.md` - 핵심 비전
- `docs/00_CORE/PROJECT_STRUCTURE.md` - 전체 구조
- `docs/04_HANDOVER/CLAUDE_인수인계_20260116_1730.md` - 최신 인수인계
- `docs/작업일정.md` - 현재 작업 계획

---

## 💡 설계 철학

### J님의 원칙
1. **사용자 개입 최소화**: 모든 것 자동화, 숨길 것만 선택
2. **카테고리 = 메뉴**: DB 카테고리가 앱/웹 메뉴로 자동 변환
3. **AI 증폭**: J님 원본이 주인공, AI는 증폭기 역할만
4. **플러그인 방식**: 새 프로젝트를 쉽게 추가 가능
5. **품질 우선**: 거짓/환각/일반론 철저히 제거

### 코드 컨벤션
- **프롬프트**: 한글 (J님 맥락 반영)
- **변수명**: snake_case
- **모델 별명**: 젠(Gemini), 진(GPT), 클로(Claude)
- **DB 경로**: `projects/{project_id}/{stage}/{doc_id}`
- **에러 처리**: Try-catch + 명확한 에러 메시지

---

## 🎓 다음 세션을 위한 요약

### 즉시 참고할 문서
1. [작업일정.md](docs/작업일정.md) - 현재 Phase 1 진행 중
2. [CLAUDE_인수인계_20260116_1730.md](docs/04_HANDOVER/CLAUDE_인수인계_20260116_1730.md) - 최신 작업 상태
3. [JNEXT_CORE_VISION.md](docs/00_CORE/JNEXT_CORE_VISION.md) - 전체 비전

### 주의사항
- 서버 시작 전 `api` 폴더로 이동 (`cd api`)
- venv 활성화: `.\venv\Scripts\Activate.ps1`
- Firebase 키 위치: JNext 루트 `jnext-service-account.json`
- "정밀분석해" 명령어는 매번 `get_hinobalance_prompt()` 호출
- 세션 학습은 10개 대화마다 자동 실행

### 핵심 명령어
```bash
# 서버 실행
cd api
.\venv\Scripts\Activate.ps1
python manage.py runserver

# DB 상태 확인
python api/scripts/check/check_balance.py

# v2 채팅 테스트
python api/scripts/test/test_v2_chat.py
```

---

**분석 완료**: 2026-01-17  
**다음 작업**: Phase 1 운동 입력 테스트 진행
