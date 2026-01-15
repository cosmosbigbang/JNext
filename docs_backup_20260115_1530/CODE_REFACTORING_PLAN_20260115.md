# JNext 코드 리팩터링 계획서

**작성일**: 2026-01-15  
**작성자**: Claude (클로)  
**목적**: views.py 2305줄 → 모듈화 및 구조 개선

---

## 📊 현재 상태 분석

### 주요 파일 라인 수
```
views.py        2,305줄  ⚠️ 너무 비대함!
views_v2.py     1,268줄  ⚠️ 역시 큼
ai_service.py     445줄  ✅ 적당
db_service.py     271줄  ✅ 적당
```

### views.py 함수 분석 (총 60+ 함수)

#### 1. 하이노밸런스 전용 API (6개)
```python
hino_review_draft()      # draft 조회
hino_review_content()    # content 조회
hino_review_raw()        # raw 조회
hino_get_detail()        # 상세 조회
hino_review_page()       # 웹 페이지
hino_auto()              # 자동화
```
**문제점**: 하이노밸런스만 하드코딩, 다른 프로젝트 확장 불가

#### 2. 채팅 관련 (3개)
```python
chat()                   # 700줄! 메인 채팅 API
save_chat_history()      # 대화 저장
load_chat_history()      # 대화 로드
```
**문제점**: chat() 함수가 700줄로 너무 비대함

#### 3. 문서 관리 (5개)
```python
get_document()           # 문서 조회
update_documents()       # 문서 수정
delete_documents()       # 문서 삭제
save_summary()           # 요약 저장
generate_final()         # 최종본 생성
```

#### 4. 명령 실행 (9개)
```python
execute_command()        # 구버전 (레거시)
execute()                # 신버전
handle_create_or_update()
handle_read()
handle_delete()
handle_create_action()
handle_read_action()
handle_update_action()
handle_delete_action()
```
**문제점**: CRUD 로직이 views.py에 직접 구현됨

### views_v2.py 함수 분석 (15개)

#### v2 채팅 시스템 (3개)
```python
chat_v2()                # 동적 맥락 채팅
save_to_raw_v2()         # RAW 저장
chat_v2_ui()             # 웹 UI
```

#### 문서 관리 v2 (8개)
```python
document_manager_ui()    # 문서 관리 페이지
search_documents()       # 검색
update_document()        # 수정
regenerate_document()    # 재생성
apply_regeneration()     # 재생성 적용
combine_documents()      # 문서 결합
delete_documents()       # 삭제
move_to_final()          # FINAL 이동
```

#### 이미지 생성 (1개)
```python
generate_image()         # DALL-E 이미지 생성
```

#### 프로젝트 관리 (2개)
```python
list_projects()          # 프로젝트 목록
create_project()         # 프로젝트 생성
```

---

## 🎯 리팩터링 목표

### 1. 파일 크기 목표
- ✅ **각 파일 최대 500줄 이하**
- ✅ **함수당 최대 100줄 이하**
- ✅ **API 엔드포인트와 비즈니스 로직 분리**

### 2. 구조 개선
- ✅ **views.py → 라우팅만** (Django View 역할)
- ✅ **비즈니스 로직 → services/** (재사용 가능)
- ✅ **DB 접근 → repositories/** (DB 추상화)
- ✅ **프로젝트별 로직 → projects/** (독립성)

### 3. 하이노밸런스 하드코딩 제거
- ✅ **모든 `hino_*` 함수 → 범용 API로 전환**
- ✅ **project_id 파라미터화**
- ✅ **다른 프로젝트 추가 시 코드 수정 없음**

---

## 📁 리팩터링 후 디렉토리 구조

```
api/api/
├── views/                          # 🆕 API 엔드포인트만 (라우팅)
│   ├── __init__.py
│   ├── chat_views.py               # 채팅 API (v1 + v2)
│   ├── document_views.py           # 문서 관리 API
│   ├── project_views.py            # 프로젝트 관리 API
│   ├── image_views.py              # 이미지 생성 API
│   ├── automation_views.py         # 자동화 API
│   └── legacy_views.py             # 레거시 API (단계적 제거)
│
├── services/                       # 🆕 비즈니스 로직 레이어
│   ├── __init__.py
│   ├── chat_service.py             # 채팅 비즈니스 로직
│   ├── document_service.py         # 문서 CRUD 로직
│   ├── regeneration_service.py     # 재생성 로직
│   ├── image_service.py            # 이미지 생성 로직
│   └── automation_service.py       # 자동화 로직
│
├── repositories/                   # 🆕 DB 접근 레이어
│   ├── __init__.py
│   ├── firestore_repository.py     # Firestore CRUD
│   ├── chat_repository.py          # 채팅 이력 저장/조회
│   └── document_repository.py      # 문서 저장/조회
│
├── core/                           # ✅ 이미 존재 (핵심 로직)
│   ├── context_manager.py          # ✅ 동적 맥락 관리
│   └── intent_classifier.py        # 🆕 의도 분류
│
├── projects/                       # ✅ 이미 존재 (프로젝트별)
│   ├── base.py                     # ✅ 기본 클래스
│   ├── hinobalance.py              # ✅ 하이노밸런스
│   └── project_manager.py          # ✅ 프로젝트 관리
│
├── ai_service.py                   # ✅ 유지 (AI 호출)
├── db_service.py                   # 🔄 → repositories/로 이동
├── meme_generator.py               # ✅ 유지
├── automation.py                   # ✅ 유지
├── error_handlers.py               # ✅ 유지
├── raw_storage.py                  # ✅ 유지
│
├── views.py                        # ⚠️ 단계적 제거 (레거시)
└── views_v2.py                     # ⚠️ 단계적 제거 (리팩터링 후)
```

---

## 🔧 리팩터링 단계별 계획

### Phase 1: 준비 작업 (1시간)
**목표**: 새 디렉토리 구조 생성 + 테스트 환경

#### 1-1. 디렉토리 생성
```bash
mkdir api/api/views
mkdir api/api/services
mkdir api/api/repositories
```

#### 1-2. __init__.py 생성
```python
# api/api/views/__init__.py
from .chat_views import *
from .document_views import *
from .project_views import *
from .image_views import *

# api/api/services/__init__.py
from .chat_service import ChatService
from .document_service import DocumentService
# ...

# api/api/repositories/__init__.py
from .firestore_repository import FirestoreRepository
from .chat_repository import ChatRepository
# ...
```

---

### Phase 2: Repository 레이어 (2시간)
**목표**: DB 접근 로직 분리

#### 2-1. firestore_repository.py 생성
**기존**: db_service.py (271줄)  
**신규**: repositories/firestore_repository.py (300줄)

```python
"""
Firestore Repository
모든 Firestore CRUD 통합
"""
class FirestoreRepository:
    
    @staticmethod
    def get_document(collection, doc_id):
        """문서 조회"""
        pass
    
    @staticmethod
    def create_document(collection, data):
        """문서 생성"""
        pass
    
    @staticmethod
    def update_document(collection, doc_id, data):
        """문서 수정"""
        pass
    
    @staticmethod
    def delete_document(collection, doc_id):
        """문서 삭제"""
        pass
    
    @staticmethod
    def query_documents(collection, filters=None, limit=50):
        """문서 검색"""
        pass
```

#### 2-2. chat_repository.py 생성
**기존**: views.py의 save_chat_history(), load_chat_history()  
**신규**: repositories/chat_repository.py (100줄)

```python
"""
Chat Repository
채팅 이력 전용 저장소
"""
class ChatRepository:
    
    @staticmethod
    def save_message(role, content, mode, model, **kwargs):
        """채팅 메시지 저장"""
        pass
    
    @staticmethod
    def load_history(limit=20):
        """채팅 이력 조회"""
        pass
    
    @staticmethod
    def clear_history():
        """채팅 이력 삭제"""
        pass
```

#### 2-3. document_repository.py 생성
**기존**: views.py, views_v2.py의 문서 CRUD  
**신규**: repositories/document_repository.py (150줄)

```python
"""
Document Repository
RAW/DRAFT/FINAL 문서 전용
"""
class DocumentRepository:
    
    @staticmethod
    def get_by_project(project_id, collection, doc_id):
        """프로젝트 문서 조회"""
        pass
    
    @staticmethod
    def search_by_project(project_id, collection, filters):
        """프로젝트 문서 검색"""
        pass
    
    @staticmethod
    def move_to_final(project_id, doc_id, from_collection):
        """FINAL로 이동"""
        pass
```

---

### Phase 3: Service 레이어 (3시간)
**목표**: 비즈니스 로직 분리

#### 3-1. chat_service.py 생성
**기존**: views.py의 chat() (700줄!)  
**신규**: services/chat_service.py (200줄)

```python
"""
Chat Service
채팅 비즈니스 로직
"""
class ChatService:
    
    def __init__(self):
        self.chat_repo = ChatRepository()
        self.context_manager = ContextManager()
    
    def process_chat(self, user_message, model, project_id, temperature, db_focus):
        """
        채팅 처리 메인 로직
        
        1. 대화 저장
        2. 대화 이력 로드
        3. 프로젝트 맥락 구성
        4. AI 호출
        5. 응답 저장
        6. 반환
        """
        # 1. 저장
        self.chat_repo.save_message('user', user_message, ...)
        
        # 2. 이력
        history = self.chat_repo.load_history()
        
        # 3. 맥락
        context = self.context_manager.build_context(...)
        
        # 4. AI
        ai_response = call_ai_model(...)
        
        # 5. 저장
        self.chat_repo.save_message('assistant', ai_response, ...)
        
        # 6. 반환
        return ai_response
```

#### 3-2. document_service.py 생성
**기존**: views.py, views_v2.py의 문서 관리 로직  
**신규**: services/document_service.py (250줄)

```python
"""
Document Service
문서 CRUD 비즈니스 로직
"""
class DocumentService:
    
    def __init__(self):
        self.doc_repo = DocumentRepository()
        self.firestore_repo = FirestoreRepository()
    
    def search_documents(self, project_id, collection, filters):
        """문서 검색"""
        return self.doc_repo.search_by_project(project_id, collection, filters)
    
    def update_document(self, project_id, collection, doc_id, data):
        """문서 수정"""
        # 검증 로직
        # 업데이트
        # 이벤트 발행 (향후 확장)
        pass
    
    def move_to_final(self, project_id, doc_id, from_collection):
        """FINAL로 이동 + 메타데이터 추가"""
        # 검증
        # 이동
        # 최종완성일, 밈/숏/전자책 필드 추가
        pass
```

#### 3-3. regeneration_service.py 생성
**기존**: views_v2.py의 regenerate_document(), apply_regeneration()  
**신규**: services/regeneration_service.py (150줄)

```python
"""
Regeneration Service
재생성 + 피드백 루프 로직
"""
class RegenerationService:
    
    def regenerate(self, project_id, collection, doc_id):
        """
        재생성 로직
        1. 프로젝트 전체 맥락 로드 (30개 문서)
        2. AI 재생성 (temperature 0.85)
        3. 기존 vs 새 내용 비교
        """
        pass
    
    def apply_with_feedback(self, project_id, collection, doc_id, feedback):
        """
        피드백 반영 재생성
        1. 피드백 분석
        2. AI 재생성 (temperature 0.3)
        3. 적용
        """
        pass
```

#### 3-4. image_service.py 생성
**기존**: views_v2.py의 generate_image()  
**신규**: services/image_service.py (100줄)

```python
"""
Image Service
이미지 생성 로직
"""
class ImageService:
    
    def generate_image(self, project_id, doc_id, prompt, size):
        """
        DALL-E 이미지 생성
        1. OpenAI API 호출
        2. Firebase Storage 업로드
        3. Firestore 메타데이터 저장
        4. URL 반환
        """
        pass
```

---

### Phase 4: View 레이어 (2시간)
**목표**: API 엔드포인트만 남기기

#### 4-1. views/chat_views.py 생성
**기존**: views.py의 chat(), chat_ui()  
**기존**: views_v2.py의 chat_v2(), chat_v2_ui()  
**신규**: views/chat_views.py (100줄)

```python
"""
Chat Views
채팅 API 엔드포인트
"""
from ..services.chat_service import ChatService

chat_service = ChatService()


@csrf_exempt
def chat(request):
    """v1 채팅 API (레거시)"""
    # 파라미터 파싱
    # chat_service.process_chat() 호출
    # JSON 반환
    pass


@csrf_exempt
def chat_v2(request):
    """v2 채팅 API (동적 맥락)"""
    # 파라미터 파싱 (temperature, db_focus 포함)
    # chat_service.process_chat() 호출
    # JSON 반환
    pass


def chat_ui(request):
    """채팅 웹 UI"""
    return render(request, 'chat.html')
```

#### 4-2. views/document_views.py 생성
**기존**: views_v2.py의 문서 관리 API 8개  
**신규**: views/document_views.py (150줄)

```python
"""
Document Views
문서 관리 API 엔드포인트
"""
from ..services.document_service import DocumentService
from ..services.regeneration_service import RegenerationService

doc_service = DocumentService()
regen_service = RegenerationService()


def document_manager_ui(request):
    """문서 관리 웹 UI"""
    return render(request, 'document_manager.html')


@csrf_exempt
def search_documents(request):
    """문서 검색 API"""
    # 파라미터 파싱
    # doc_service.search_documents() 호출
    # JSON 반환
    pass


@csrf_exempt
def regenerate_document(request):
    """재생성 API"""
    # regen_service.regenerate() 호출
    pass


@csrf_exempt
def move_to_final(request):
    """FINAL 이동 API"""
    # doc_service.move_to_final() 호출
    pass
```

#### 4-3. views/project_views.py 생성
**기존**: views_v2.py의 list_projects(), create_project()  
**신규**: views/project_views.py (50줄)

```python
"""
Project Views
프로젝트 관리 API
"""
from ..projects.project_manager import project_manager


@csrf_exempt
def list_projects(request):
    """프로젝트 목록 API"""
    projects = project_manager.list_projects()
    return JsonResponse({'projects': projects})


@csrf_exempt
def create_project(request):
    """프로젝트 생성 API"""
    # project_manager.create_project() 호출
    pass
```

#### 4-4. views/image_views.py 생성
**기존**: views_v2.py의 generate_image()  
**신규**: views/image_views.py (50줄)

```python
"""
Image Views
이미지 생성 API
"""
from ..services.image_service import ImageService

image_service = ImageService()


@csrf_exempt
def generate_image(request):
    """이미지 생성 API"""
    # image_service.generate_image() 호출
    pass
```

---

### Phase 5: URL 라우팅 정리 (1시간)
**목표**: urls.py 깔끔하게 정리

#### 5-1. api/config/urls.py 수정
```python
"""
JNext 메인 URL 라우팅
"""
from django.urls import path, include

urlpatterns = [
    # 채팅 API
    path('api/chat/', include('api.views.chat_views')),
    
    # 문서 관리 API
    path('api/documents/', include('api.views.document_views')),
    
    # 프로젝트 관리 API
    path('api/projects/', include('api.views.project_views')),
    
    # 이미지 생성 API
    path('api/images/', include('api.views.image_views')),
    
    # 자동화 API
    path('api/automation/', include('api.views.automation_views')),
]
```

---

### Phase 6: 하이노밸런스 하드코딩 제거 (1시간)
**목표**: 모든 `hino_*` 함수를 범용 API로 전환

#### 6-1. 기존 하이노밸런스 전용 API 제거
```python
# ❌ 제거 대상
hino_review_draft()
hino_review_content()
hino_review_raw()
hino_get_detail()
hino_review_page()
hino_auto()
```

#### 6-2. 범용 API로 대체
```python
# ✅ 신규 범용 API
GET /api/documents/?project=hinobalance&collection=draft
GET /api/documents/?project=hinobalance&collection=final
GET /api/documents/{doc_id}/?project=hinobalance
GET /api/automation/?project=hinobalance&action=integrate
```

**장점**:
- 다른 프로젝트 추가 시 코드 수정 없음
- URL만으로 프로젝트 선택 가능
- 프로젝트별 독립성 확보

---

### Phase 7: 테스트 및 검증 (2시간)
**목표**: 리팩터링 후 기능 정상 동작 확인

#### 7-1. 단위 테스트
```python
# tests/test_chat_service.py
def test_chat_service_process():
    service = ChatService()
    result = service.process_chat(
        user_message="안녕",
        model="gemini-pro",
        project_id="hinobalance",
        temperature=0.85,
        db_focus=50
    )
    assert result['answer']
```

#### 7-2. 통합 테스트
```python
# tests/test_document_views.py
def test_search_documents_api():
    response = client.get('/api/documents/?project=hinobalance')
    assert response.status_code == 200
```

#### 7-3. 수동 테스트
- 채팅 페이지 접속
- 문서 관리 페이지 접속
- 재생성 테스트
- 이미지 생성 테스트

---

### Phase 8: 레거시 코드 제거 (1시간)
**목표**: views.py, views_v2.py 완전 제거

#### 8-1. 단계적 제거
1. views.py → views/legacy_views.py 이동 (백업)
2. views_v2.py → 삭제
3. 모든 import 경로 수정
4. 테스트 통과 확인
5. legacy_views.py도 최종 삭제

---

## 📊 리팩터링 전후 비교

### Before (현재)
```
views.py              2,305줄  ⚠️
views_v2.py           1,268줄  ⚠️
─────────────────────────────
Total                 3,573줄
```

### After (목표)
```
views/
  chat_views.py         100줄  ✅
  document_views.py     150줄  ✅
  project_views.py       50줄  ✅
  image_views.py         50줄  ✅
  automation_views.py    50줄  ✅

services/
  chat_service.py       200줄  ✅
  document_service.py   250줄  ✅
  regeneration_service  150줄  ✅
  image_service.py      100줄  ✅

repositories/
  firestore_repository  300줄  ✅
  chat_repository.py    100줄  ✅
  document_repository   150줄  ✅
─────────────────────────────
Total                 1,650줄  (54% 감소!)
```

**추가 효과**:
- ✅ 코드 중복 제거 (500줄 이상)
- ✅ 테스트 가능성 향상
- ✅ 유지보수성 향상
- ✅ 확장성 확보 (새 프로젝트 추가 용이)

---

## ⏱️ 전체 일정

| Phase | 작업 | 예상 시간 | 우선순위 |
|-------|------|-----------|----------|
| 1 | 준비 작업 | 1시간 | 🔴 최우선 |
| 2 | Repository 레이어 | 2시간 | 🔴 최우선 |
| 3 | Service 레이어 | 3시간 | 🔴 최우선 |
| 4 | View 레이어 | 2시간 | 🟡 중요 |
| 5 | URL 라우팅 정리 | 1시간 | 🟡 중요 |
| 6 | 하이노 하드코딩 제거 | 1시간 | 🟢 보통 |
| 7 | 테스트 및 검증 | 2시간 | 🔴 최우선 |
| 8 | 레거시 코드 제거 | 1시간 | 🟢 보통 |

**총 예상 시간**: 13시간  
**권장 일정**: 2일 (하루 6-7시간)

---

## 🎯 다음 단계 (리팩터링 이후)

### 1. 콘텐츠 자동화 파이프라인 구축
- 밈 시나리오 생성
- 밈 이미지 + 자막 제작
- 숏폼 영상 제작
- 전자책 조립

### 2. 프로젝트 확장
- 모의고사 앱 (ExamNavi)
- JBody 신체 분석
- JFaceAge 얼굴 나이 분석
- JStyle 패션 스타일링

### 3. 성능 최적화
- DB 쿼리 최적화
- 캐싱 시스템 도입
- AI API 호출 최적화

---

## 💡 J님께 질문

1. **리팩터링 시작 시점**: 지금 바로 시작할까요, 아니면 하이노밸런스 문서 40개 정리 후?
2. **우선순위**: Phase 1-3 (Repository + Service)만 먼저? 아니면 전체 Phase 1-8 한번에?
3. **하이노 하드코딩**: 완전 제거 vs 호환성 유지 (기존 URL도 작동)?

**제 추천**:
- ✅ **하이노밸런스 문서 정리 완료 후** 리팩터링 시작
- ✅ Phase 1-3 먼저 (Repository + Service) → 안정화 → Phase 4-8
- ✅ 하이노 URL 호환성 유지 (기존 앱/웹 영향 없음)

J님의 의견을 들려주세요! 🚀
