# JNext

AI가 직접 DB를 제어하는 시스템 - Django Backend + Firebase Firestore

**비전**: J님의 무한한 창의성을 손실 없이 저장하고, AI 증폭을 통해 최종 상품(앱, 웹, 전자책, 밈, 숏폼)으로 자동 변환하는 범용 플랫폼

---

## ⚡ 새 클로드 빠른 파악 (3분 컷)

### 1️⃣ 지금 뭐하는 프로젝트?
- **RAW → DRAFT → FINAL** 3단계 AI 증폭으로 J님 아이디어를 자동 상품화
- **현재 Phase 1**: 하이노밸런스 운동 2~3개 입력하며 시스템 테스트 중
- **내 역할**: "클로" (별명) = 하이노밸런스 전문 AI

### 2️⃣ 필수 문서 3개만
1. **[작업일정.md](docs/작업일정.md)** ← 지금 뭐 해야 하는지
2. **[CLAUDE_인수인계_20260116_1730.md](docs/04_HANDOVER/CLAUDE_인수인계_20260116_1730.md)** ← 이전 클로드가 뭐 했는지
3. **[SYSTEM_ANALYSIS_20260117.md](docs/00_CORE/SYSTEM_ANALYSIS_20260117.md)** ← 전체 시스템 86개 파일 분석

### 3️⃣ 핵심 파일 위치
```
api/api/
├── ai_config.py          # 내 프롬프트 여기 있음 (get_hinobalance_prompt)
├── views_v2.py           # "정밀분석해" 명령어 처리
└── session_learning.py   # 세션 학습 (10개 대화마다 자동 요약)

docs/
├── 00_CORE/AI_ONBOARDING/PROMPT_클로.md  # 내 정체성
└── 작업일정.md           # 현재 할 일
```

### 4️⃣ 서버 시작 (복붙용)
```bash
cd api
.\venv\Scripts\Activate.ps1
python manage.py runserver
```

### 5️⃣ J님 호칭 규칙
- ✅ 항상 "J님"으로 호칭
- ✅ 존댓말 사용
- ❌ "사용자님", "고객님" 금지

---

## 📚 문서 가이드

### 핵심 문서
- **[00_CORE/](docs/00_CORE/)** - 프로젝트 비전, 아키텍처, AI 프롬프트
  - [JNEXT_CORE_VISION.md](docs/00_CORE/JNEXT_CORE_VISION.md) - 3단계 AI 증폭 전략
  - [PROJECT_STRUCTURE.md](docs/00_CORE/PROJECT_STRUCTURE.md) - 전체 파일 구조
- **[01_DESIGN/](docs/01_DESIGN/)** - 시스템 설계 및 AI 전략
  - [DESIGN_DOCUMENT.md](docs/01_DESIGN/DESIGN_DOCUMENT.md) - 전체 설계서
  - [AI_MODEL_STRATEGY.md](docs/01_DESIGN/AI_MODEL_STRATEGY.md) - Gemini/GPT/Claude 전략
- **[02_ROADMAP/](docs/02_ROADMAP/)** - 단계별 로드맵
  - [JNEXT_ROADMAP.md](docs/02_ROADMAP/JNEXT_ROADMAP.md) - 밈/숏폼/전자책 파이프라인
- **[04_HANDOVER/](docs/04_HANDOVER/)** - 인수인계 문서
  - [CLAUDE_인수인계_20260116_1730.md](docs/04_HANDOVER/CLAUDE_인수인계_20260116_1730.md) - 최신 작업 상태

### 현재 작업 계획
📋 [작업일정.md](docs/작업일정.md) 참조
- **Phase 1** (진행 중): 신규 운동 2~3개 등록 및 테스트
- **Phase 2** (예정): 전체 이론/운동 정리 (draft → final)
- **Phase 3** (예정): 전자책 출판 준비

## 프로젝트 구조

```
JNext/
├── api/                        # Django 백엔드
│   ├── api/                   # Django 앱 (AI, DB, 프로젝트 관리)
│   ├── config/                # Django 설정
│   ├── scripts/               # 범용 유틸리티
│   └── manage.py
├── projects/                  # 프로젝트별 데이터/스크립트
│   └── hinobalance/          # 첫 번째 프로젝트
│       ├── data/             # 원본 데이터
│       ├── scripts/          # 전용 스크립트
│       └── docs/
├── docs/                      # 전체 문서 (00_CORE ~ 07_OPERATIONS)
├── hinobalance_mobile/       # HinoBalance 모바일 앱 (Flutter)
├── jnext_mobile/             # JNext 범용 모바일 앱 (Flutter)
└── jnext-service-account.json # Firebase 키 (Git 제외)
```

## 빠른 시작

### 1. 백엔드 서버 실행

```bash
cd api
.\venv\Scripts\Activate.ps1
python manage.py runserver
```

### 2. Firebase 설정

1. Firebase Console에서 서비스 계정 키 다운로드
2. `jnext-service-account.json`으로 저장
3. JNext 루트 폴더에 배치

### 3. API 테스트

- http://localhost:8000/ - API 정보
- http://localhost:8000/api/test/ - Firebase 연결 테스트
- http://localhost:8000/api/v2/chat/ - v2 채팅 API (정밀분석 기능)

## 최신 기능 (2026-01-16)

### ✨ 세션 학습 시스템
AI가 대화에서 자동으로 학습하여 다음 세션에 반영
- **자동 학습**: 대화 10개마다 자동 요약 저장
- **수동 학습**: "학습정리" 명령어로 즉시 요약
- **학습 반영**: "정밀분석해" 시 최근 3개 학습 내용 적용

### 🎯 정밀분석해 명령어
특수 명령어로 7개 항목 구조화 분석 생성
1. 본질 분석
2. 효과
3. 대상
4. 동작 요약
5. 평점
6. 장단점
7. 개선점

### 🔄 Native History 패턴
Gemini, GPT, Claude 모두 메시지 리스트 직접 전달로 컨텍스트 관리 최적화

## 기술 스택

- **Backend**: Django 6.0
- **Database**: Firebase Firestore
- **Python**: 3.14
- **AI Models**: Gemini Pro/Flash, GPT-4o, Claude
- **Mobile**: Flutter (hinobalance_mobile, jnext_mobile)

## 데이터 플로우

```
RAW (1차 AI 증폭)
  ↓
DRAFT (2차 AI 증폭)
  ↓
FINAL (최종 확정)
  ↓
상품 출시 (앱/웹/전자책/밈/숏폼)
```

Firestore: `projects/{project_id}/{raw|draft|final}/{doc_id}`

## 보안

⚠️ **절대 커밋하지 말 것:**
- `*-service-account.json`
- `.env` 파일

## 개발자

J님 & Claude

## 라이선스

Private
