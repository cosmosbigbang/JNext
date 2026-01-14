# JNext 프로젝트 구조 설계서

**작성일**: 2026-01-13  
**목적**: JNext 범용화 및 코드 리팩터링 설계  
**버전**: 2.0 - JNext v2 완성 반영  
**최종 업데이트**: 2026-01-13 오후

---

## 📊 현재 구조 분석 (As-Is)

### 문제점

#### 1. views.py 비대화
- **총 2384줄** - 모든 로직이 한 파일에 집중
- **32개 함수** - 체계 없이 나열
- API 엔드포인트, 비즈니스 로직, DB 접근이 분리 안됨
- 유지보수 및 확장성 저하

#### 2. 하이노밸런스 하드코딩
- `hino_*` 컬렉션명이 코드 전반에 하드코딩
- 변수명, 함수명에 `hino` 접두어 남발
- 다른 프로젝트 추가 시 전면 수정 필요

#### 3. Firestore 구조 문제
```
현재 (Flat 구조):
hino_raw/           # 루트 컬렉션
hino_draft/         # 루트 컬렉션
hino_content/       # 루트 컬렉션
chat_history/       # 루트 컬렉션
```

**문제**:
- 프로젝트 구분 불가
- 컬렉션 이름 충돌 가능성
- 다중 프로젝트 운영 불가

#### 4. 기능 분리 미흡

**기존 파일 구조**:
```
backend/api/
├── views.py              # ❌ 2384줄 - 모든 것
├── ai_service.py         # ✅ AI 호출 (잘 분리됨)
├── db_service.py         # △ DB 접근 (부분 분리)
├── meme_generator.py     # ✅ 밈 생성 (독립적)
├── automation.py         # ✅ 자동화 (독립적)
└── error_handlers.py     # ✅ 에러 처리 (독립적)
```

### 현재 주요 함수 목록

**views.py 함수 분류** (32개):

1. **하이노밸런스 전용 API** (6개)
   - `hino_review_draft()` - draft 조회
   - `hino_review_content()` - content 조회
   - `hino_review_raw()` - raw 조회
   - `hino_get_detail()` - 상세 조회
   - `hino_review_page()` - 웹 페이지
   - `hino_auto()`, `hino_status()` - 자동화

2. **채팅 관련** (3개)
   - `chat()` - 메인 채팅 API (700줄!)
   - `save_chat_history()` - 대화 저장
   - `load_chat_history()` - 대화 로드

3. **문서 관리** (5개)
   - `get_document()` - 문서 조회
   - `update_documents()` - 문서 수정
   - `delete_documents()` - 문서 삭제
   - `save_summary()` - 요약 저장
   - `generate_final()` - 최종본 생성

4. **명령 실행** (8개)
   - `execute_command()` - 구버전
   - `execute()` - 신버전
   - `handle_create_or_update()` - CRUD Create/Update
   - `handle_read()` - CRUD Read
   - `handle_delete()` - CRUD Delete
   - `handle_create_action()` - Action Create
   - `handle_read_action()` - Action Read
   - `handle_update_action()` - Action Update
   - `handle_delete_action()` - Action Delete

5. **유틸리티** (5개)
   - `now_kst()` - 한국 시간
   - `determine_save_targets()` - 저장 대상 결정
   - `search_firestore()` - Firestore 검색
   - `verify_api_key()` - API 키 검증
   - `index()`, `chat_ui()` - UI 렌더링

6. **기타** (5개)
   - `firebase_test()` - Firebase 테스트
   - `system_logs_list()` - 로그 조회

---

## 🎯 목표 구조 (To-Be)

### 설계 원칙

1. **관심사 분리** (Separation of Concerns)
   - API 라우팅 vs 비즈니스 로직 vs 데이터 접근
   
2. **프로젝트 독립성**
   - 각 프로젝트는 독립적인 설정 파일로 관리
   - 새 프로젝트 추가 시 기존 코드 수정 최소화

3. **확장성**
   - 플러그인 방식으로 프로젝트 추가
   - 공통 로직 재사용

4. **테스트 가능성**
   - 각 모듈 독립적으로 테스트 가능

### 디렉토리 구조

```
backend/
├── api/
│   ├── views.py                    # 📍 API 엔드포인트만 (라우팅)
│   ├── urls.py                     # URL 매핑
│   ├── ai_service.py              # ✅ AI 호출 (유지)
│   ├── db_service.py              # 🔄 DB 접근 강화
│   ├── meme_generator.py          # ✅ 밈 생성 (유지)
│   ├── automation.py              # ✅ 자동화 (유지)
│   ├── error_handlers.py          # ✅ 에러 처리 (유지)
│   │
│   ├── core/                      # 🆕 핵심 비즈니스 로직
│   │   ├── __init__.py
│   │   ├── intent_handler.py      # 의도 분류 및 라우팅
│   │   ├── chat_service.py        # 채팅 비즈니스 로직
│   │   ├── document_service.py    # 문서 CRUD 로직
│   │   └── project_manager.py     # 🔥 프로젝트 관리 (핵심!)
│   │
│   ├── projects/                  # 🆕 프로젝트별 설정
│   │   ├── __init__.py
│   │   ├── base.py                # BaseProject 클래스
│   │   ├── hinobalance.py         # 하이노밸런스 프로젝트
│   │   ├── exam_navi.py           # 모의고사 앱 (미래)
│   │   ├── project_a.py           # 신규 프로젝트 A
│   │   ├── project_b.py           # 신규 프로젝트 B
│   │   └── project_c.py           # 신규 프로젝트 C
│   │
│   └── utils/                     # 🆕 유틸리티
│       ├── __init__.py
│       ├── time_utils.py          # now_kst() 등
│       ├── validators.py          # 데이터 검증
│       └── formatters.py          # 포맷팅
│
├── config/
│   ├── settings.py                # Django 설정
│   └── urls.py                    # 루트 URL
│
└── templates/
    ├── chat.html                  # JNext 채팅 UI
    └── hino_review.html           # 하이노밸런스 리뷰 페이지
```

---

## 🔥 핵심: Project Manager 설계

### BaseProject 클래스

**파일**: `api/projects/base.py`

```python
from abc import ABC, abstractmethod
from typing import Dict, List, Optional

class BaseProject(ABC):
    """모든 프로젝트의 베이스 클래스"""
    
    # 프로젝트 메타데이터
    project_id: str = "base"
    display_name: str = "기본 프로젝트"
    description: str = ""
    
    # Firestore 컬렉션 구조
    collections = {
        'raw': 'raw',
        'draft': 'draft',
        'content': 'content'
    }
    
    # 컨텐츠 타입 정의
    content_types: List[str] = []
    
    # 필드 매핑 (한글 <-> 영문)
    field_mapping: Dict[str, str] = {
        'category': '카테고리',
        'title': '제목',
        'content': '내용',
        'full_text': '전체글',
        'created_at': '작성일시',
        'status': '상태'
    }
    
    # AI 프롬프트 템플릿
    system_prompts: Dict[str, str] = {}
    
    def get_collection_path(self, stage: str) -> str:
        """
        Firestore 컬렉션 경로 반환
        
        Args:
            stage: 'raw', 'draft', 'content'
            
        Returns:
            str: "projects/{project_id}/{stage}"
        """
        return f"projects/{self.project_id}/{self.collections[stage]}"
    
    def get_field_name(self, english_key: str) -> str:
        """영문 키를 프로젝트별 필드명으로 변환"""
        return self.field_mapping.get(english_key, english_key)
    
    @abstractmethod
    def validate_document(self, data: dict) -> tuple[bool, str]:
        """
        문서 데이터 검증
        
        Returns:
            (is_valid, error_message)
        """
        pass
    
    @abstractmethod
    def get_system_prompt(self, mode: str) -> str:
        """
        모드별 AI 시스템 프롬프트 반환
        
        Args:
            mode: 'organize', 'hybrid', 'analysis'
        """
        pass
```

### HinoBalanceProject 클래스

**파일**: `api/projects/hinobalance.py`

```python
from .base import BaseProject

class HinoBalanceProject(BaseProject):
    """하이노밸런스 프로젝트"""
    
    project_id = "hinobalance"
    display_name = "하이노밸런스"
    description = "J님의 하이노밸런스 운동 이론 및 실전 관리"
    
    # 컨텐츠 타입
    content_types = [
        'theory_integrated',  # 통합이론
        'category_theory',    # 카테고리별 이론
        'exercise',           # 실전 운동
        'meme_scenario'       # 밈 시나리오
    ]
    
    # 카테고리 목록
    categories = [
        '하이노워킹',
        '하이노스케이팅',
        '하이노골반',
        '하이노워밍',
        '하이노철봉',
        '하이노풋삽'
    ]
    
    # 필드 매핑 (한글 우선)
    field_mapping = {
        'category': '카테고리',
        'title': '제목',
        'content': '내용',
        'full_text': '전체글',
        'exercise_name': '운동명',
        'content_type': 'content_type',
        'created_at': '작성일시',
        'status': '데이터상태'
    }
    
    # AI 프롬프트
    system_prompts = {
        'organize': """당신은 하이노밸런스 전문 AI입니다.
J님의 운동 이론과 실전 내용을 정리합니다.
사실 중심, 정확성 우선, 환각 최소화.""",
        
        'hybrid': """당신은 하이노밸런스 전문 AI입니다.
이론과 실전을 결합하여 답변합니다.""",
        
        'analysis': """당신은 하이노밸런스 창의적 분석가입니다.
운동의 의미와 가치를 창의적으로 해석합니다."""
    }
    
    def validate_document(self, data: dict) -> tuple[bool, str]:
        """문서 검증"""
        # 필수 필드 체크
        required_fields = ['카테고리', '내용']
        
        for field in required_fields:
            if field not in data or not data[field]:
                return False, f"필수 필드 누락: {field}"
        
        # 카테고리 유효성 체크
        if data['카테고리'] not in self.categories:
            return False, f"유효하지 않은 카테고리: {data['카테고리']}"
        
        return True, ""
    
    def get_system_prompt(self, mode: str) -> str:
        """모드별 프롬프트 반환"""
        return self.system_prompts.get(mode, self.system_prompts['hybrid'])
```

### ProjectManager 클래스

**파일**: `api/core/project_manager.py`

```python
from typing import Dict, Optional
from ..projects.base import BaseProject
from ..projects.hinobalance import HinoBalanceProject
# 미래: from ..projects.exam_navi import ExamNaviProject

class ProjectManager:
    """프로젝트 관리 싱글톤"""
    
    _instance = None
    _projects: Dict[str, BaseProject] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize_projects()
        return cls._instance
    
    def _initialize_projects(self):
        """등록된 프로젝트 초기화"""
        self.register_project(HinoBalanceProject())
        # 미래: self.register_project(ExamNaviProject())
    
    def register_project(self, project: BaseProject):
        """프로젝트 등록"""
        self._projects[project.project_id] = project
        print(f"[ProjectManager] Registered: {project.display_name}")
    
    def get_project(self, project_id: str) -> Optional[BaseProject]:
        """프로젝트 가져오기"""
        return self._projects.get(project_id)
    
    def list_projects(self) -> Dict[str, str]:
        """프로젝트 목록 반환 {id: display_name}"""
        return {
            pid: proj.display_name 
            for pid, proj in self._projects.items()
        }
    
    def get_default_project(self) -> BaseProject:
        """기본 프로젝트 반환 (하이노밸런스)"""
        return self._projects.get('hinobalance')

# 싱글톤 인스턴스
project_manager = ProjectManager()
```

---

## 📦 Firestore 마이그레이션

### 변경 전 (Flat)

```
Firestore Root/
├── hino_raw/
│   └── {doc_id}
├── hino_draft/
│   └── {doc_id}
├── hino_content/
│   └── {doc_id}
└── chat_history/
    └── {chat_id}
```

### 변경 후 (Nested)

```
Firestore Root/
├── projects/
│   ├── hinobalance/
│   │   ├── raw/
│   │   │   └── {doc_id}
│   │   ├── draft/
│   │   │   └── {doc_id}
│   │   └── content/
│   │       └── {doc_id}
│   │
│   ├── exam_navi/
│   │   ├── questions/
│   │   │   └── {doc_id}
│   │   └── exams/
│   │       └── {doc_id}
│   │
│   └── project_a/
│       └── ...
│
└── chat_history/
    └── {session_id}/
        └── messages/
            ├── {msg_id}
            │   ├── role: "user"
            │   ├── content: "..."
            │   ├── project: "hinobalance"  # 🔥 어떤 프로젝트 대화인지
            │   ├── mode: "hybrid"
            │   └── timestamp: ...
```

### 마이그레이션 스크립트

**파일**: `backend/migrate_to_nested.py`

```python
from firebase_admin import firestore
from api.db_service import FirestoreService

def migrate_hinobalance():
    """하이노밸런스 데이터를 Nested 구조로 마이그레이션"""
    
    db = FirestoreService.get_client()
    
    # 1. hino_raw → projects/hinobalance/raw
    print("Migrating hino_raw...")
    migrate_collection(db, 'hino_raw', 'projects/hinobalance/raw')
    
    # 2. hino_draft → projects/hinobalance/draft
    print("Migrating hino_draft...")
    migrate_collection(db, 'hino_draft', 'projects/hinobalance/draft')
    
    # 3. hino_content → projects/hinobalance/content
    print("Migrating hino_content...")
    migrate_collection(db, 'hino_content', 'projects/hinobalance/content')
    
    print("✅ Migration complete!")

def migrate_collection(db, old_path, new_path):
    """컬렉션 데이터 복사"""
    docs = db.collection(old_path).stream()
    
    for doc in docs:
        data = doc.to_dict()
        # 새 경로에 복사
        db.collection(new_path).document(doc.id).set(data)
        print(f"  Copied: {doc.id}")

if __name__ == "__main__":
    migrate_hinobalance()
```

---

## 🎨 UI 변경

### chat.html 프로젝트 선택 추가

```html
<div class="controls">
    <!-- 🆕 프로젝트 선택 -->
    <select id="project-select" class="project-select">
        <option value="hinobalance" selected>🏃 하이노밸런스</option>
        <option value="exam_navi">📝 모의고사</option>
        <option value="project_a">🆕 프로젝트 A</option>
    </select>
    
    <!-- 기존 모드/모델 선택 -->
    <select id="mode-toggle" class="mode-toggle">
        <option value="organize">📊 DB 모드</option>
        <option value="hybrid" selected>🔀 통합 모드</option>
        <option value="analysis">💬 대화 모드</option>
    </select>
    
    <select id="model-select" class="model-select">
        <option value="gemini-pro" selected>⚡ 젠 (정확)</option>
        <option value="gemini-flash">🚀 젠시 (빠름)</option>
        <option value="gpt">💡 진 (창의)</option>
        <option value="claude">👑 클로 (코딩)</option>
    </select>
</div>
```

### JavaScript 수정

```javascript
// 프로젝트 선택 시
document.getElementById('project-select').addEventListener('change', (e) => {
    currentProject = e.target.value;
    loadProjectSettings(currentProject);
});

// API 호출 시 프로젝트 포함
fetch('/api/v1/chat/', {
    method: 'POST',
    body: JSON.stringify({
        message: userMessage,
        mode: currentMode,
        model: currentModel,
        project: currentProject  // 🔥 추가
    })
})
```

---

## 📋 리팩터링 단계별 계획

### Phase 1: 구조 설계 ✅
- [x] 현재 구조 분석
- [x] 목표 구조 설계
- [x] STRUCTURE.md 작성

### Phase 2: 핵심 모듈 개발 ✅ (2026-01-13 완료!)
- [x] `api/projects/base.py` 작성
- [x] `api/projects/hinobalance.py` 작성
- [x] `api/projects/project_manager.py` 작성
- [x] `api/core/context_manager.py` 작성 (핵심!)
- [x] `api/views_v2.py` 작성
- [x] `templates/chat_v2.html` 작성
- [x] UI 개선: 프로젝트 선택 통합

### 향후 추가 예정 프로젝트
- [ ] **모의고사앱** (`exam`) - 수능/공무원 모의고사 생성
- [ ] **JBody** (`jbody`) - 신체 분석 및 관리
- [ ] **JFaceAge** (`jfaceage`) - 얼굴 나이 분석
- [ ] **JStyle** (`jstyle`) - 스타일 추천

### Phase 3: views.py 분리 (오늘~내일)
- [ ] `api/core/intent_handler.py` 작성
- [ ] `api/core/chat_service.py` 작성
- [ ] `api/core/document_service.py` 작성
- [ ] `views.py` 슬림화 (엔드포인트만 남기기)

### Phase 4: Firestore 마이그레이션 (내일)
- [ ] 백업 스크립트 작성
- [ ] 마이그레이션 스크립트 작성
- [ ] 테스트 데이터로 검증
- [ ] 실제 데이터 마이그레이션
- [ ] 구버전 컬렉션 삭제

### Phase 5: UI 업데이트 (내일)
- [ ] chat.html 프로젝트 선택 추가
- [ ] JavaScript 수정
- [ ] 모바일 앱 연동

### Phase 6: 테스트 및 배포 (모레)
- [ ] 기존 기능 동작 확인
- [ ] 새 프로젝트 추가 테스트
- [ ] Render 배포

---

## 🚀 확장 시나리오

### 신규 프로젝트 추가 예시

**파일**: `api/projects/exam_navi.py`

```python
from .base import BaseProject

class ExamNaviProject(BaseProject):
    """모의고사 앱 프로젝트"""
    
    project_id = "exam_navi"
    display_name = "모의고사 네비게이터"
    description = "수능/공무원 모의고사 생성 및 관리"
    
    collections = {
        'questions': 'questions',  # 문제 은행
        'exams': 'exams',          # 모의고사
        'results': 'results'       # 성적 분석
    }
    
    content_types = [
        'multiple_choice',  # 객관식
        'essay',            # 서술형
        'true_false'        # O/X
    ]
    
    # ... (나머지 구현)
```

**등록**:
```python
# api/core/project_manager.py
from ..projects.exam_navi import ExamNaviProject

def _initialize_projects(self):
    self.register_project(HinoBalanceProject())
    self.register_project(ExamNaviProject())  # 🔥 추가!
```

**끝!** 기존 코드 수정 없이 새 프로젝트 추가 완료!

---

## 📌 주요 설계 결정 사항

### 1. 왜 Nested 구조?
- **장점**: 프로젝트 격리, 확장성, 관리 용이
- **단점**: 쿼리 복잡도 증가 → ProjectManager로 추상화 해결

### 2. 왜 chat_history는 루트에?
- 프로젝트 간 대화 흐름 추적 필요
- 한 대화에서 여러 프로젝트 전환 가능
- 세션 관리 단순화

### 3. 왜 BaseProject 추상 클래스?
- 인터페이스 강제 (validate_document, get_system_prompt 필수)
- 공통 로직 재사용 (get_collection_path)
- 타입 안정성 확보

### 4. 왜 ProjectManager 싱글톤?
- 앱 전역에서 동일한 프로젝트 인스턴스 사용
- 메모리 효율성
- 초기화 1회만 수행

---

## ⚠️ 주의사항

### 마이그레이션 시
1. **반드시 백업** - Firestore Export 필수
2. **테스트 환경 먼저** - 작은 데이터로 검증
3. **롤백 계획** - 실패 시 복구 방법 준비
4. **점진적 이행** - 한 번에 모든 기능 바꾸지 말기

### 코드 작성 시
1. **타입 힌트 사용** - Python 3.10+ 타입 힌팅
2. **docstring 작성** - 모든 public 함수에 문서화
3. **테스트 작성** - 핵심 로직은 단위 테스트 필수

---

## � 일반적인 문제 및 디버깅 가이드

> **출처**: `claude_guide.md` (젠 작성, 2026-01-14)

### 문제 1: API 수정했는데 반영 안 됨

**증상**: 코드를 수정했는데도 이전처럼 동작  
**사례**: `GEMINI_API_ISSUE` (2026-01-14 해결)

**원인**: Django 개발 서버가 코드 변경을 감지하지 못하고 메모리에 남은 이전 버전 실행

**해결 절차**:
1. **프로세스 완전 종료**: `Ctrl+C` → 포트 확인 (`Get-NetTCPConnection -LocalPort 8000`) → 좀비 프로세스 강제 종료 (`Stop-Process -Id <ID> -Force`)
2. **파이썬 캐시 삭제**: `backend/` 폴더 내 모든 `__pycache__` 디렉토리 삭제
3. **서버 재시작**: 위 두 단계 후 `python manage.py runserver`

### 문제 2: API가 400 Bad Request 또는 예상치 못한 오류 반환

**원인**: 수정한 코드가 아닌 **옛날 코드**로 요청이 전달됨

**해결 절차 (URL 라우팅 추적)**:
1. **시작점**: `backend/config/urls.py` → 요청 URL이 어떤 `include()`로 연결되는지 확인
2. **중간점**: `backend/api/urls.py` → 최종 뷰 함수/클래스 찾기
3. **종착점**: 해당 뷰 파일 → 최신 로직 호출하는지 확인

**예시**:
```python
# config/urls.py
path('api/v2/chat/', include('api.urls'))

# api/urls.py
path('chat/', views_v2.chat_v2, name='chat_v2')

# views_v2.py
def chat_v2(request):
    return call_ai_model(...)  # ← 이게 정말 ai_service.py 호출하는지 확인!
```

### 문제 3: 여러 AI 모델 SDK 충돌

**특징**: Gemini, GPT, Claude 등 여러 SDK 사용으로 인한 파라미터 형식 차이

**주요 이슈**:
- **Gemini**: `config` 파라미터는 dict 아닌 `types.GenerateContentConfig` 객체 사용 (camelCase!)
  ```python
  # ❌ 잘못된 방법
  config={'system_instruction': '...', 'temperature': 0.5}
  
  # ✅ 올바른 방법
  from google.genai import types
  config=types.GenerateContentConfig(
      systemInstruction='...',  # camelCase!
      temperature=0.5,
      maxOutputTokens=32768,
      responseMimeType='application/json'
  )
  ```
- **Claude**: `proxies` 인자 관련 오류 (Python 3.14 호환성 이슈)
- 각 AI 서비스가 올바른 클라이언트와 설정 사용하는지 교차 확인 필수

---

## �📚 참고 자료

### Django 모범 사례
- Fat Models, Thin Views
- Service Layer 패턴
- Repository 패턴

### Firebase/Firestore
- [Firestore 데이터 모델링](https://firebase.google.com/docs/firestore/data-model)
- [컬렉션 그룹 쿼리](https://firebase.google.com/docs/firestore/query-data/queries#collection-group-query)

### Python 디자인 패턴
- Singleton Pattern
- Factory Pattern
- Strategy Pattern

---

**마지막 업데이트**: 2026-01-13  
**작성자**: Claude with J님  
**상태**: 설계 완료, 구현 대기
