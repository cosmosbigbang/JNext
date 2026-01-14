# JNext & HinoBalance 설계서

**작성일**: 2026-01-13  
**작성자**: J님 + Claude  
**목적**: GPT-4o(진), Gemini(젠) 자문용

---

## 📋 목차
1. [프로젝트 개요](#프로젝트-개요)
2. [시스템 아키텍처](#시스템-아키텍처)
3. [기술 스택](#기술-스택)
4. [핵심 개념](#핵심-개념)
5. [데이터 플로우](#데이터-플로우)
6. [API 설계](#api-설계)
7. [프로젝트 구조](#프로젝트-구조)
8. [하이노밸런스 상세 설계](#하이노밸런스-상세-설계)
9. [향후 확장 계획](#향후-확장-계획)

---

## 프로젝트 개요

### JNext - 범용 창의 자동화 플랫폼

**비전**
> J님의 무한한 창의성을 손실 없이 저장하고, AI 증폭을 통해 최종 상품(앱, 웹, 전자책, 밈, 숏폼)으로 자동 변환하는 범용 플랫폼

**핵심 목표**
1. **1차 목표**: 창의성 저장 - 아이디어 손실 방지
2. **2차 목표**: 자동화 - 앱/웹/전자책/밈/숏 자동 제작

**특징**
- 플러그인 방식의 프로젝트 시스템
- 동적 컨텍스트 관리 (ContextManager)
- RAW → DRAFT → FINAL 3단계 AI 증폭
- 카테고리 = 메뉴 자동화

### HinoBalance - 첫 번째 테스트 케이스

**정의**: 균형 잡힌 하체 운동 앱

**역할**: JNext 플랫폼의 첫 번째 플러그인 프로젝트

---

## 시스템 아키텍처

```
┌─────────────────────────────────────────────────────────────┐
│                         JNext v2                            │
│                    (범용 플랫폼)                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐      ┌──────────────┐                   │
│  │ Context      │      │  Project     │                   │
│  │ Manager      │◄─────┤  Manager     │                   │
│  │              │      │              │                   │
│  │ • 대화 15%   │      │ • 플러그인   │                   │
│  │ • 프로젝트   │      │   등록       │                   │
│  │   15-85%     │      │ • 동적 로딩  │                   │
│  │ • 일반 나머지│      └──────┬───────┘                   │
│  │ • 온도 제어  │             │                           │
│  └──────────────┘             │                           │
│                               │                           │
│              ┌────────────────┴─────────────────┐         │
│              │                                  │         │
│      ┌───────▼───────┐              ┌───────────▼──────┐ │
│      │ BaseProject   │              │  Future Projects │ │
│      │  (추상 클래스) │              │  • ExamNavi     │ │
│      └───────┬───────┘              │  • JBody        │ │
│              │                      │  • JFaceAge     │ │
│      ┌───────▼───────┐              │  • JStyle       │ │
│      │HinoBalance    │              └─────────────────┘ │
│      │Project        │                                  │
│      │• project_id   │                                  │
│      │• 시스템 프롬프트│                                  │
│      │• DB 컨텍스트  │                                  │
│      │• 메뉴 구조    │                                  │
│      └───────────────┘                                  │
│                                                          │
└──────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    데이터 레이어                             │
├─────────────────────────────────────────────────────────────┤
│  Firebase Firestore                                        │
│                                                             │
│  hino_raw/        hino_draft/       hino_final/            │
│  ├─ 원본          ├─ 정리본         ├─ 최종본              │
│  ├─ 1차 AI 증폭   ├─ 2차 AI 증폭    ├─ 상품 출시           │
│  └─ 자동 분류     └─ 카테고리 확정  └─ 앱/웹 메뉴         │
│                                                             │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    프론트엔드                                │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐         ┌──────────────┐                 │
│  │  웹 UI      │         │  모바일 앱    │                 │
│  │ (Django)    │         │  (Flutter)   │                 │
│  │             │         │              │                 │
│  │ • 듀얼 패널 │         │ • jnext_     │                 │
│  │ • 슬라이더  │         │   mobile     │                 │
│  │ • 프로젝트  │         │ • hinobalance│                 │
│  │   선택      │         │   _mobile    │                 │
│  └─────────────┘         └──────────────┘                 │
└─────────────────────────────────────────────────────────────┘
```

---

## 기술 스택

### Backend
```yaml
Framework: Django 6.0
Language: Python 3.14
Database:
  - Firestore (Firebase) - 메인 DB
  - SQLite - 로컬 캐시/세션
Authentication: Firebase Admin SDK
API: REST + JSON
Deployment: Render.com
```

### Frontend
```yaml
Web:
  Framework: Django Templates
  Style: 듀얼 패널 레이아웃
  
Mobile:
  Framework: Flutter
  Language: Dart
  Apps:
    - jnext_mobile (범용)
    - hinobalance_mobile (하이노 전용)
```

### AI Models
```yaml
Primary:
  - Gemini Pro/Flash (젠/젠시)
  - GPT-4o (진)
  - Claude Sonnet 4.5 (클로)
  
Libraries:
  - google-generativeai
  - openai
  - anthropic
```

---

## 핵심 개념

### 1. 동적 컨텍스트 관리

**ContextManager** (`backend/api/core/context_manager.py`)

```python
class ContextManager:
    """
    슬라이더 값(0-100)에 따라 AI 컨텍스트와 온도를 동적 조정
    """
    
    def build_context(self, focus: int, project_id: str = None):
        """
        Args:
            focus: 0-100 집중도 슬라이더
            project_id: 프로젝트 ID (None = 일반 대화)
        
        Returns:
            {
                'weights': {
                    'conversation': 15,      # 대화 이력 가중치
                    'project': 15-85,        # 프로젝트 DB 가중치 (focus에 비례)
                    'general': 나머지        # 일반 지식 가중치
                },
                'temperature': 0.2-0.7       # 창의성 온도 (focus에 반비례)
            }
        """
```

**가중치 계산 공식**
```python
conversation_weight = 15  # 고정
project_weight = int(15 + (focus * 0.7))  # 15-85%
general_weight = 100 - conversation_weight - project_weight
temperature = 0.7 - (focus / 100 * 0.5)  # 0.7 → 0.2
```

**예시**
| Focus | 대화 | 프로젝트 | 일반 | 온도 |
|-------|------|----------|------|------|
| 0     | 15%  | 15%      | 70%  | 0.70 |
| 50    | 15%  | 50%      | 35%  | 0.45 |
| 100   | 15%  | 85%      | 0%   | 0.20 |

---

### 2. 플러그인 프로젝트 시스템

**BaseProject** (`backend/api/projects/base.py`)

```python
class BaseProject(ABC):
    """모든 프로젝트의 추상 기본 클래스"""
    
    @property
    @abstractmethod
    def project_id(self) -> str:
        """프로젝트 고유 ID"""
        pass
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """AI 시스템 프롬프트"""
        pass
    
    @abstractmethod
    def get_db_context(self, query: str) -> str:
        """DB에서 관련 컨텍스트 로드"""
        pass
    
    def get_menu_structure(self) -> dict:
        """앱/웹 메뉴 구조 (선택)"""
        return {}
```

**ProjectManager** (`backend/api/projects/project_manager.py`)

```python
class ProjectManager:
    """싱글톤 패턴의 프로젝트 레지스트리"""
    
    _instance = None
    _projects = {}
    
    def register_project(self, project: BaseProject):
        """새 프로젝트 등록"""
        self._projects[project.project_id] = project
    
    def get_project(self, project_id: str) -> BaseProject:
        """프로젝트 조회"""
        return self._projects.get(project_id)
```

---

### 3. 3단계 AI 증폭

```
┌─────────────────────────────────────────────────────────────┐
│ RAW (원본 + 1차 증폭)                                        │
├─────────────────────────────────────────────────────────────┤
│ 입력: J님의 원본 대화/아이디어                                │
│                                                             │
│ AI 처리:                                                    │
│   • 대화 분석 → 컬렉션 자동 선택                             │
│   • 또는 명령으로 컬렉션 생성                                │
│   • 원본 보존 + 초기 구조화                                  │
│                                                             │
│ 저장: hino_raw 컬렉션                                       │
└─────────────────────────────────────────────────────────────┘
                        ▼
┌─────────────────────────────────────────────────────────────┐
│ DRAFT (2차 증폭 - 정리)                                      │
├─────────────────────────────────────────────────────────────┤
│ 입력: 복수의 RAW 데이터                                      │
│                                                             │
│ AI 처리:                                                    │
│   • 총론 작성 (전체 개요)                                    │
│   • 각론 정리 (개별 항목)                                    │
│   • 최종 카테고리 확정 ★★★                                  │
│                                                             │
│ 저장: hino_draft 컬렉션                                     │
│                                                             │
│ 핵심: 이 카테고리가 앱/웹 메뉴가 됨!                         │
└─────────────────────────────────────────────────────────────┘
                        ▼
┌─────────────────────────────────────────────────────────────┐
│ FINAL (최종 확정 → 상품 출시)                                │
├─────────────────────────────────────────────────────────────┤
│ 입력: DRAFT 최종본                                          │
│                                                             │
│ 자동화 실행:                                                │
│   ✓ 앱 자동 생성 (Flutter)                                  │
│   ✓ 웹 자동 생성 (Django)                                   │
│   ✓ 전자책 자동 생성 (PDF/EPUB)                             │
│   ✓ 밈 자동 생성 (이미지)                                    │
│   ✓ 숏폼 자동 생성 (영상)                                    │
│                                                             │
│ 저장: hino_final 컬렉션                                     │
└─────────────────────────────────────────────────────────────┘
```

---

### 4. 카테고리 = 메뉴 자동화

**핵심 인사이트**
> "모든 카테고리가 곧 메뉴야" - J님

**자동화 흐름**
```
1. RAW 단계
   └─ AI가 대화 분석 → 컬렉션 선택/생성

2. DRAFT 단계
   └─ 최종 카테고리 확정 ★

3. FINAL 단계
   └─ 확정된 카테고리 → 앱/웹 메뉴 자동 생성
```

**Default 철학**
- 모든 카테고리는 기본적으로 표시됨
- 사용자는 "숨김" 액션만 수행
- 최소 개입 원칙

---

## 데이터 플로우

### 사용자 대화 → 최종 상품

```
┌──────────┐
│  사용자  │ "하이노 골반 운동에 대해 알려줘"
└────┬─────┘
     │
     ▼
┌──────────────────────────────────────┐
│  JNext v2 API                        │
│  /api/v2/chat/                       │
├──────────────────────────────────────┤
│ 1. 프로젝트 로드                      │
│    project = ProjectManager.get(     │
│        "hino"                        │
│    )                                 │
│                                      │
│ 2. 컨텍스트 빌드                      │
│    context = ContextManager.build(   │
│        focus=50,                     │
│        project_id="hino"             │
│    )                                 │
│                                      │
│ 3. AI 호출                           │
│    response = ai_service.generate(   │
│        system=project.get_system_    │
│                 prompt(),            │
│        context=project.get_db_       │
│                 context(query),      │
│        temperature=context['temp']   │
│    )                                 │
│                                      │
│ 4. RAW 저장 (선택)                   │
│    firestore.save(                   │
│        collection="hino_raw",        │
│        data=response                 │
│    )                                 │
└──────────────────────────────────────┘
     │
     ▼
┌──────────────────────────────────────┐
│  Firebase Firestore                  │
├──────────────────────────────────────┤
│  hino_raw/골반운동001                 │
│  {                                   │
│    "content": "골반 운동은...",       │
│    "category": "골반",                │
│    "timestamp": "2026-01-13",        │
│    "ai_analyzed": true               │
│  }                                   │
└──────────────────────────────────────┘
     │
     ▼ (배치 처리)
┌──────────────────────────────────────┐
│  DRAFT 생성                          │
│  /api/v2/draft/generate              │
├──────────────────────────────────────┤
│  • 복수 RAW 데이터 수집               │
│  • AI 2차 증폭 (총론/각론)            │
│  • 카테고리 확정: "골반"              │
└──────────────────────────────────────┘
     │
     ▼
┌──────────────────────────────────────┐
│  hino_draft/골반_총론                 │
│  {                                   │
│    "title": "골반 운동 가이드",       │
│    "category": "골반",                │
│    "sections": [...]                 │
│  }                                   │
└──────────────────────────────────────┘
     │
     ▼ (승인 후)
┌──────────────────────────────────────┐
│  FINAL 자동화                        │
│  /api/v2/final/publish               │
├──────────────────────────────────────┤
│  ✓ Flutter 앱 메뉴 생성:             │
│    "골반" 카테고리 추가               │
│                                      │
│  ✓ 웹 메뉴 생성:                     │
│    /hino/category/골반                │
│                                      │
│  ✓ 전자책 생성:                      │
│    "하이노 골반 운동 완전 정복.pdf"   │
│                                      │
│  ✓ 밈/숏폼 생성:                     │
│    골반운동_밈001.jpg                 │
│    골반운동_숏001.mp4                 │
└──────────────────────────────────────┘
```

---

## API 설계

### v2 API 엔드포인트

#### 1. 채팅 API
```http
POST /api/v2/chat/
Content-Type: application/json

Request:
{
  "message": "하이노 골반 운동 알려줘",
  "project": "hino",
  "focus": 50,
  "model": "gemini-pro",
  "session_id": "uuid-1234"
}

Response:
{
  "response": "골반 운동은...",
  "context_used": {
    "conversation": 15,
    "project": 50,
    "general": 35
  },
  "temperature": 0.45,
  "source": "hino_final → hino_draft → hino_raw"
}
```

#### 2. RAW 저장 API
```http
POST /api/v2/save-raw/
Content-Type: application/json

Request:
{
  "project": "hino",
  "content": "골반 운동 내용...",
  "auto_categorize": true
}

Response:
{
  "id": "raw_001",
  "collection": "hino_raw",
  "suggested_category": "골반",
  "confidence": 0.95
}
```

#### 3. 프로젝트 목록 API
```http
GET /api/v2/projects/

Response:
{
  "projects": [
    {
      "id": "hino",
      "name": "하이노밸런스",
      "description": "균형 잡힌 하체 운동",
      "status": "active"
    },
    {
      "id": "exam",
      "name": "모의고사앱",
      "description": "AI 기반 맞춤 문제 생성",
      "status": "planned"
    }
  ]
}
```

#### 4. 컨텍스트 테스트 API
```http
POST /api/v2/test/
Content-Type: application/json

Request:
{
  "focus": 50,
  "project": "hino"
}

Response:
{
  "weights": {
    "conversation": 15,
    "project": 50,
    "general": 35
  },
  "temperature": 0.45,
  "context_preview": "최근 대화: ...\n프로젝트 DB: ...\n"
}
```

---

## 프로젝트 구조

```
JNext/
├── .github/
│   └── copilot-instructions.md      # AI 에이전트 가이드
│
├── backend/
│   ├── api/
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   └── context_manager.py   # 동적 컨텍스트 관리
│   │   │
│   │   ├── projects/
│   │   │   ├── __init__.py
│   │   │   ├── base.py              # BaseProject 추상 클래스
│   │   │   ├── hinobalance.py       # HinoBalance 구현
│   │   │   └── project_manager.py   # 싱글톤 레지스트리
│   │   │
│   │   ├── views.py                 # v1 레거시 API
│   │   └── views_v2.py              # v2 신규 API
│   │
│   ├── config/
│   │   ├── settings.py              # Django 설정
│   │   ├── urls.py                  # URL 라우팅
│   │   └── wsgi.py
│   │
│   ├── templates/
│   │   ├── chat_v2.html             # v2 웹 UI
│   │   └── ...
│   │
│   ├── static/                      # CSS, JS, 이미지
│   │
│   ├── manage.py
│   ├── requirements.txt
│   └── render.yaml                  # Render 배포 설정
│
├── jnext_mobile/                    # Flutter 범용 앱
│   ├── lib/
│   │   └── main.dart
│   └── pubspec.yaml
│
├── hinobalance_mobile/              # Flutter 하이노 전용 앱
│   ├── lib/
│   │   └── main.dart
│   └── pubspec.yaml
│
├── jnext-service-account.json       # Firebase 인증 (절대 커밋 금지!)
│
├── JNEXT_CORE_VISION.md             # 핵심 비전 문서
├── STRUCTURE.md                     # 구조 분석
├── SECURITY_SCHEDULE.md             # 보안 점검 스케줄
└── README.md
```

---

## 하이노밸런스 상세 설계

### 프로젝트 정보

```python
# backend/api/projects/hinobalance.py

class HinoBalanceProject(BaseProject):
    @property
    def project_id(self) -> str:
        return "hino"
    
    def get_system_prompt(self) -> str:
        return """
        당신은 하이노밸런스 전문 AI 트레이너입니다.
        
        역할:
        - 균형 잡힌 하체 운동 가이드
        - 개인 맞춤형 운동 프로그램 제공
        - 안전하고 효과적인 운동 방법 안내
        
        중요 규칙:
        - 항상 J님으로 호칭
        - 안전을 최우선으로
        - 과학적 근거 기반 설명
        
        데이터 우선순위:
        1. hino_final (최종 검증된 내용)
        2. hino_draft (정리된 내용)
        3. hino_raw (원본 아이디어)
        """
```

### 카테고리 구조

```python
categories = {
    'theory_integrated': '통합이론',  # 전체 이론 통합
    'category_theory': '이론',        # 개별 이론
    'exercise_detailed': '실전',      # 실전 운동
    'meme_scenario': '밈스토리',      # 밈 시나리오
    'sitcom_episode': '시트콤회차',   # 시트콤 에피소드
    'sitcom_scene': '시트콤장면',     # 시트콤 씬
    'meme': '밈이미지',               # 완성 밈
    'short': '숏폼',                  # 숏폼 영상
}
```

### 메뉴 아이콘

```python
category_icons = {
    'theory_integrated': Icons.book,
    'category_theory': Icons.category,
    'exercise_detailed': Icons.fitness_center,
    'meme_scenario': Icons.emoji_emotions,
    'sitcom_episode': Icons.tv,
    'sitcom_scene': Icons.movie,
    'meme': Icons.image,
    'short': Icons.video_library,
}
```

### 데이터 로딩 우선순위

```python
def get_db_context(self, query: str) -> str:
    """
    1. hino_final 검색 (최종 승인된 콘텐츠)
    2. hino_draft 검색 (정리된 콘텐츠)
    3. hino_raw 검색 (원본 아이디어)
    
    Returns: 가장 관련성 높은 콘텐츠 (최대 3개)
    """
```

### 모바일 앱 특징

**hinobalance_mobile**
- 전용 브랜딩
- 카테고리별 필터링
- Draft/Content/Raw 소스 선택
- 상세 모달 뷰
- 호버 시 리뷰 표시

---

## 향후 확장 계획

### 1. ExamNavi (모의고사앱)

```python
class ExamNaviProject(BaseProject):
    project_id = "exam"
    
    categories = {
        'math': '수학',
        'english': '영어',
        'science': '과학',
        'history': '역사'
    }
    
    # AI가 문제 자동 분류
    # 난이도별 자동 구성
    # 맞춤형 문제 생성
```

### 2. JBody (건강 관리)

```python
class JBodyProject(BaseProject):
    project_id = "jbody"
    
    categories = {
        'upper': '상체',
        'lower': '하체',
        'cardio': '유산소',
        'stretch': '스트레칭'
    }
```

### 3. JFaceAge (얼굴 나이 분석)

```python
class JFaceAgeProject(BaseProject):
    project_id = "jfaceage"
    
    categories = {
        'teens': '10대',
        'twenties': '20대',
        'thirties': '30대',
        'analysis': '분석 결과'
    }
```

### 4. JStyle (패션 스타일링)

```python
class JStyleProject(BaseProject):
    project_id = "jstyle"
    
    categories = {
        'casual': '캐주얼',
        'formal': '정장',
        'sports': '스포츠',
        'street': '스트릿'
    }
```

---

## 자문 요청 사항

### 진(GPT-4o)에게

1. **코드 품질 개선**
   - ContextManager 로직 최적화 방안
   - ProjectManager 싱글톤 패턴 개선점
   - API 응답 속도 향상 방안

2. **확장성**
   - 프로젝트 100개 이상 확장 시 고려사항
   - 대규모 트래픽 처리 전략
   - 캐싱 전략

3. **보안**
   - API 인증 개선 방안
   - 민감 데이터 처리 best practice
   - CORS 설정 최적화

### 젠(Gemini)에게

1. **AI 통합 최적화**
   - Gemini Pro/Flash 활용 극대화 방안
   - 프롬프트 엔지니어링 개선
   - RAG(Retrieval-Augmented Generation) 최적화

2. **자동화 전략**
   - 카테고리 자동 분류 정확도 향상
   - 밈/숏폼 자동 생성 파이프라인
   - 전자책 자동 생성 로직

3. **사용자 경험**
   - 슬라이더 기반 컨텍스트 조정 UX 개선
   - 실시간 피드백 시스템
   - 개인화 알고리즘

### 클로(Claude)에게 - 현재 역할

- 전체 아키텍처 설계 및 구현
- 문서화 및 가이드 작성
- 코드 리뷰 및 최적화
- J님과의 직접 협업

---

## 현재 상태

### 완료 ✅
- [x] JNext v2 코어 시스템
- [x] ContextManager 구현
- [x] ProjectManager 구현
- [x] HinoBalance 프로젝트 구현
- [x] v2 API 엔드포인트
- [x] 웹 UI (chat_v2.html)
- [x] 모바일 앱 (jnext_mobile, hinobalance_mobile)
- [x] 카테고리 명명 개선
- [x] 보안 설정
- [x] Git/Render 배포

### 진행 중 🔄
- [ ] 로컬 웹 테스트
- [ ] Render 배포 검증
- [ ] 성능 최적화

### 계획 📋
- [ ] Firestore 마이그레이션
- [ ] ExamNavi 프로젝트 추가
- [ ] JBody 프로젝트 추가
- [ ] 밈/숏폼 자동 생성 파이프라인
- [ ] 전자책 자동 생성 기능

---

**작성 완료일**: 2026-01-13  
**버전**: 1.0  
**다음 업데이트**: 진과 젠의 피드백 반영 후
