# JNext 프로젝트 구조 문서

**최종 업데이트**: 2026-01-16 14:30  
**버전**: 2.0 (리팩터링 완료)

---

## 📂 전체 구조 개요

```
JNext/
├── api/                         # Django Backend
├── projects/                   # 프로젝트별 데이터/스크립트
├── docs/                       # 전체 문서
├── apps/                       # Flutter 앱 (향후)
├── hinobalance_mobile/        # 모바일 앱
├── jnext_mobile/              # 모바일 앱
├── meme_images/               # 밈 이미지
└── jnext-service-account.json # Firebase 키
```

---

## 🔧 Backend (api/)

### 구조
```
api/
├── api/                       # Django 앱
│   ├── views.py              # 기본 API
│   ├── views_v2.py           # v2 채팅 API (정밀분석)
│   ├── ai_config.py          # AI 설정 중앙 관리
│   ├── ai_service.py         # AI 모델 호출
│   ├── db_service.py         # Firestore 연동
│   ├── core/                 # 핵심 모듈
│   │   └── context_manager.py # Native History 관리
│   ├── projects/             # 프로젝트별 설정
│   │   ├── base.py
│   │   ├── hinobalance.py
│   │   └── project_manager.py
│   └── ...
│
├── config/                   # Django 설정
│   ├── settings.py
│   ├── urls.py
│   └── asgi.py
│
├── scripts/                  # 범용 유틸리티 (40개)
│   ├── check/               # DB 상태 확인 (13개)
│   │   ├── check_balance.py
│   │   ├── check_chat_v2.py
│   │   └── ...
│   ├── test/                # API 테스트 (7개)
│   │   ├── test_chat_api.py
│   │   ├── test_v2_chat.py
│   │   └── ...
│   └── utils/               # 기타 도구 (20개)
│       ├── content_generator.py
│       ├── migrate_firestore.py
│       └── ...
│
├── static/                  # 정적 파일
├── templates/               # HTML 템플릿
│   └── chat_v2.html
├── manage.py
├── requirements.txt
└── db.sqlite3
```

### 핵심 파일

#### ai_config.py
```python
MODEL_ALIASES = {
    'gemini-pro': '젠',
    'gpt': '진',
    'claude': '클로'
}

TEMPERATURE_SETTINGS = {
    'v2': 0.5  # 정밀분석 기본값
}

HINOBALANCE_SYSTEM_PROMPT = """..."""  # 7개 항목 강제
GENERAL_SYSTEM_PROMPT = """..."""      # 일반 대화
```

#### views_v2.py
```python
# "정밀분석해" 감지
if "정밀분석해" in user_message:
    system_prompt = ai_config.HINOBALANCE_SYSTEM_PROMPT
else:
    system_prompt = ai_config.GENERAL_SYSTEM_PROMPT
```

---

## 📊 Projects (projects/)

### HinoBalance 프로젝트 구조

```
projects/hinobalance/
├── README.md                  # 프로젝트 가이드
│
├── data/                      # 원본 데이터 (25개)
│   ├── theory/               # 카테고리별 이론 (6개)
│   │   ├── category_theory_하이노골반.txt
│   │   ├── category_theory_하이노스케이팅.txt
│   │   ├── category_theory_하이노워밍.txt
│   │   ├── category_theory_하이노워킹.txt
│   │   ├── category_theory_하이노철봉.txt
│   │   └── category_theory_하이노풋삽.txt
│   │
│   ├── exercises/            # 개별 운동 설명 (15개)
│   │   ├── exercise_하이노골반돌리기.txt
│   │   ├── exercise_하이노골반벌리기.txt
│   │   ├── exercise_하이노골반상하.txt
│   │   ├── exercise_하이노골반좌우.txt
│   │   ├── exercise_하이노스케이팅전진.txt
│   │   ├── exercise_하이노스케이팅좌우.txt
│   │   ├── exercise_하이노스케이팅코너웍.txt
│   │   ├── exercise_하이노워밍벤치.txt
│   │   ├── exercise_하이노워킹전진.txt
│   │   ├── exercise_하이노워킹주먹.txt
│   │   ├── exercise_하이노워킹크로스.txt
│   │   ├── exercise_하이노워킹퐁당퐁당.txt
│   │   ├── exercise_하이노철봉한손.txt
│   │   ├── exercise_하이노풋삽벽두손.txt
│   │   └── exercise_하이노풋삽벽한손.txt
│   │
│   └── combined/             # 통합 이론 문서 (4개)
│       ├── theory_combined.txt
│       ├── theory_integrated_full.txt
│       ├── theory_medium.txt
│       └── theory_summary.txt
│
├── scripts/                  # 전용 스크립트 (14개)
│   ├── analyze.py           # DB 전체 분석
│   ├── create.py            # 데이터 생성 템플릿
│   ├── publishing.py        # Draft→Final 변환
│   ├── delete_all_hino.py
│   ├── fix_hino_titles.py
│   ├── combine_theory.py
│   ├── create_category_theories.py
│   │
│   ├── upload/              # Firestore 업로드 (4개)
│   │   ├── upload_hino_001.py
│   │   ├── upload_hino_015_020.py
│   │   ├── upload_hino_021_022.py
│   │   └── upload_hino_batch.py
│   │
│   └── organize/            # 데이터 정리 (2개)
│       ├── exercises.py
│       └── theory.py
│
└── docs/
    └── HINO_API_EXAMPLES.md
```

### 향후 확장 패턴
```
projects/
├── hinobalance/              # Phase 1
├── exam_navi/                # Phase 2 (미래)
└── jbody/                    # Phase 3 (미래)
```

---

## 📚 Documentation (docs/)

### 폴더 구조
```
docs/
├── 00_CORE/                 # 핵심 설계 문서
├── 01_DESIGN/               # 설계 스펙
├── 02_ROADMAP/              # 로드맵
├── 03_CONTENT/              # 콘텐츠
├── 04_HANDOVER/             # 인수인계 문서
│   ├── CLAUDE_인수인계_*.md
│   └── WORK_HISTORY.md
├── 05_CONVERSATIONS/        # 대화 기록
├── 06_LEGACY/               # 레거시
├── 07_OPERATIONS/           # 운영
│
├── 작업일정.md              # 작업 일정
├── 구조변경_2026-01-16.md  # 리팩터링 기록
├── prompt_진.md             # GPT 프롬프트
├── prompt_젠.md             # Gemini 프롬프트
└── ...
```

### 주요 문서
- **작업일정.md**: Phase 1/2/3 계획
- **구조변경_*.md**: 구조 변경 이력
- **CLAUDE_인수인계_*.md**: 세션 종료 시 작성
- **prompt_*.md**: AI 모델별 프롬프트

---

## 🗄️ Database (Firestore)

### Collection 구조
```
projects/
├── hinobalance/
│   ├── raw/                 # AI 초안 저장
│   ├── draft/               # 개선 필요 문서
│   └── final/               # 출판 완료 문서
├── exam_navi/
└── jbody/

chat_history/                # 채팅 기록 (Native History)
├── {session_id}/
│   └── messages/
```

### 문서 구조 (hinobalance)
```json
{
  "title": "하이노워킹전진",
  "category": "하이노워킹",
  "content": "...",
  "analysis": "...",
  "effects": "...",
  "target": "...",
  "movement_summary": "...",
  "rating": 4.5,
  "pros_cons": "...",
  "improvements": "...",
  "timestamp": "2026-01-16T14:30:00Z"
}
```

---

## 🔄 워크플로우

### 1. 데이터 입력 (Phase 1)
```
운동 설명 입력
    ↓
"정밀분석해" 명령
    ↓
AI가 7개 항목 생성
    ↓
raw 컬렉션 저장
```

### 2. 문서 정리 (Phase 2)
```
raw 문서 검토
    ↓
좋은 문서 → final
나쁜 문서 → draft
    ↓
draft → publishing.py → final
```

### 3. 출판 (Phase 3)
```
final 문서 수집
    ↓
E-book 형식 변환
    ↓
모바일 앱 배포
```

---

## 🛠️ 개발 환경

### Requirements
- Python 3.14
- Django 6.0
- Firebase Admin SDK
- Google Generative AI
- OpenAI API
- Anthropic API

### 실행
```bash
cd api
python manage.py runserver
# http://localhost:8000/chat/v2/
```

### 테스트
```bash
cd api
python manage.py check
python scripts/test/test_v2_chat.py
```

---

## 📈 버전 히스토리

### v2.0 (2026-01-16)
- ✅ 폴더 기반 구조로 리팩터링
- ✅ projects/hinobalance/ 분리
- ✅ api/scripts/ 범용 유틸 정리
- ✅ 경로 수정 및 검증 완료

### v1.5 (2026-01-16)
- ✅ "정밀분석해" 특수 명령어
- ✅ 7개 항목 응답 형식 강제
- ✅ Temperature 0.5 조정
- ✅ Native History 적용

### v1.0 (2026-01-15)
- ✅ Django + Firebase 기본 구조
- ✅ 3개 AI 모델 통합
- ✅ 프로젝트 매니저 구현

---

## 🔗 참조 링크

- **Firebase Console**: https://console.firebase.google.com
- **Django Docs**: https://docs.djangoproject.com/en/6.0/
- **프로젝트 README**: `projects/hinobalance/README.md`
- **작업 일정**: `docs/작업일정.md`

---

**최종 업데이트**: 2026-01-16 14:30  
**총 파일 수**: 150+ (리팩터링 후)  
**프로젝트 상태**: ✅ Phase 1 준비 완료
