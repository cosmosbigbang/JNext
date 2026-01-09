# JNext 시스템 백업 문서 (2026-01-09)

> **작성자**: J님 & 클로  
> **목적**: VS Code 재시작 시 시스템 상태 복원용 백업

---

## 📌 프로젝트 개요

**하이노밸런스 전용 자연어 기반 CRUD 시스템**

- **백엔드**: Django 6.0 + Firebase Firestore + Gemini AI
- **모바일**: Flutter (Android/iOS)
- **핵심 기능**: 자연어 입력 → AI가 의도 분류 → 자동 CRUD 실행
- **현재 단계**: 검증·테스트 단계 (새 기능 추가 금지)

---

## 🎯 시스템 구조

### 1. 백엔드 (Django)

**경로**: `c:\Projects\JNext\backend\`

**핵심 파일**:
- `config/settings.py` - Django 설정 + Firebase/Gemini 초기화
- `config/urls.py` - API 라우팅
- `api/views.py` - 모든 API 엔드포인트 (1545줄)
- `api/ai_service.py` - AI 모델 호출 + 의도 분류 (279줄)
- `.env` - 환경 변수 (Firebase 키, Gemini API 키)
- `jnext-service-account.json` - Firebase 인증 키 (Git 제외)

**서버 실행**:
```powershell
cd C:\Projects\JNext\backend
.\venv\Scripts\Activate.ps1
python manage.py runserver
# http://localhost:8000
```

---

### 2. 모바일 (Flutter)

**경로**: `c:\Projects\JNext\jnext_mobile\`

**핵심 파일**:
- `lib/main.dart` - 메인 앱 (652줄)
  - `ChatScreen` - 채팅 화면
  - `SearchScreen` - 문서 검색 화면

**API 연결**:
- URL: `http://192.168.219.139:8000/api/v1/chat/`
- USB 연결 시 PC IP 사용

---

## 🔥 Firebase Firestore 구조

### 컬렉션 3단계

1. **`hino_raw`** - 원본/아이디어
2. **`hino_draft`** - 정리 중
3. **`hino_final`** - 최종 완성본

### 문서 필드 구조

```json
{
  "제목": "문서 제목",
  "카테고리": "하이노이론 | 하이노워킹 | 하이노스케이팅 | 하이노철봉 | 하이노기본 | 하이노밸런스",
  "운동명": "하이노워킹기본 | 하이노워킹패스트 | 하이노워킹슬로우 | ...",
  "내용": "요약본 (500자 내외)",
  "전체글": "출판용 전체 글 (2000-5000자, 마크다운)",
  "원본질문": "J님이 물어본 원본 질문",
  "AI응답": { JSON 구조화된 AI 답변 },
  "원본문서수": 3,
  "데이터상태": "DRAFT | FINAL",
  "작성일시": "2026-01-09T12:34:56+09:00",
  "수정일시": "2026-01-09T12:34:56+09:00",
  "작성자": "J님 | J님 (자동저장) | J님 (AI 종합)",
  "종류": "정리 | 최종본"
}
```

### 시스템 로그

- **컬렉션**: `system_logs`
- **용도**: 시스템 초기화, 오류 기록

---

## 🤖 AI 시스템 (Gemini)

### 모델 정보

- **모델**: `models/gemini-2.5-flash`
- **API**: Google AI (google.genai)
- **설정**: `config/settings.py`에서 초기화

### 3가지 모드

#### 1. **DB 모드 (organize)** - 엄격
- 데이터베이스에 있는 것만 작업
- DB에 없으면 거부 (`missing_info`)
- 시스템 프롬프트: `ORGANIZE_SYSTEM_PROMPT`
- 아이콘: 📦 (파란색)

#### 2. **통합 모드 (hybrid)** ⭐ - 기본값
- **DB + 현재 대화 세션 분석 통합 정리**
- 사용 시나리오:
  1. 대화 모드에서 브레인스토밍
  2. 통합 모드로 전환
  3. DB 정보 + 방금 대화 유력 분석 → **섞어서 정리**
  4. "저장해" → 통합본 저장
- Evidence: DB / 현재 대화 세션 / 통합 정리
- 시스템 프롬프트: `HYBRID_SYSTEM_PROMPT`
- 아이콘: 🔀 (초록색)

#### 3. **대화 모드 (analysis)** - 자유로움
- J님 아이디어 중심 (DB 참고)
- 제한적 일반 지식 허용
- 환각 통제: 사실 기반만
- 시스템 프롬프트: `ANALYSIS_SYSTEM_PROMPT`
- 아이콘: 💬 (보라색)

### AI 응답 스키마 (JSON 강제)

```json
{
  "answer": "J님에게 보여줄 최종 답변",
  "claims": ["핵심 주장 1", "핵심 주장 2"],
  "evidence": [
    {
      "claim": "주장",
      "collection": "hino_draft",
      "doc_id": "abc123",
      "field": "내용",
      "value": "근거 내용"
    }
  ],
  "missing_info": ["DB에 없는 정보"],
  "confidence": 0.85,
  "actions_suggested": [
    {
      "action": "CREATE | UPDATE | DELETE",
      "collection": "hino_draft",
      "reason": "이유"
    }
  ]
}
```

---

## 🎬 자연어 의도 분류 (Intent Classification)

**파일**: `api/ai_service.py` - `classify_intent()` 함수

### 지원하는 의도 (Intent)

#### 1. **SAVE** (저장)
- **키워드**: 저장, save, 저장해, 저장해줘, 기록, 보관
- **동작**:
  - 마지막 AI 답변을 Firestore에 자동 저장
  - 요약본(내용) + 출판용 전체 글(전체글) 생성
  - Gemini가 출판용 전체 글 자동 작성
- **예시**: "저장해", "이거 보관해줘"

#### 2. **READ** (조회)
- **키워드**: 검색, 가져와, 보여줘, 조회, show, 찾아줘, 목록
- **제외 키워드**: 알려, 설명, 분석, 어때, 뭐야 (AI 대화용)
- **동작**:
  - 카테고리/컬렉션 필터링
  - 문서 목록 반환
  - `document_list` 필드로 체크박스 UI용 데이터 제공
- **예시**: "하이노워킹 보여줘", "draft 목록 가져와"

#### 3. **UPDATE** (수정)
- **키워드**: 수정, update, 고쳐, 바꿔, 변경
- **동작**: 여러 문서 일괄 수정
- **예시**: "이거 수정해"

#### 4. **DELETE** (삭제)
- **키워드**: 삭제, delete, 지워, 제거
- **동작**: 여러 문서 일괄 삭제
- **예시**: "이거 지워"

#### 5. **GENERATE_FINAL** (최종본 생성)
- **키워드**: 최종본, 정리해, 종합해, 통합해, 만들어
- **동작**:
  - 조건에 맞는 draft/raw 문서 검색
  - Gemini가 여러 문서를 통합 정리
  - hino_final에 저장
- **파라미터**:
  - `category` - 카테고리 감지
  - `exercise_name` - 운동명 감지
  - `include_keywords` - 포함 키워드
  - `exclude_keywords` - 제외 키워드
- **예시**: "하이노워킹 기본 패스트 포함해서 최종본 만들어"

#### 6. **NONE** (일반 질문)
- **동작**: AI와 대화 (organize/analysis 모드)
- **예시**: "하이노워킹이 뭐야?"

---

## 📡 API 엔드포인트

**기본 URL**: `http://localhost:8000`

### 메인 API

#### 1. `POST /api/v1/chat/`
**메인 통합 API** (모든 기능 여기서 처리)

**요청**:
```json
{
  "message": "사용자 메시지",
  "mode": "organize | analysis"
}
```

**응답**:
```json
{
  "status": "success",
  "action": "SAVE | READ | UPDATE | DELETE | GENERATE_FINAL | NONE",
  "message": "✅ 실행 결과 메시지",
  "response": {
    "answer": "AI 답변",
    "claims": [...],
    "evidence": [...],
    "missing_info": [...],
    "confidence": 0.85
  },
  "document_list": [
    {
      "collection": "hino_draft",
      "doc_id": "abc123",
      "title": "제목",
      "category": "하이노워킹",
      "preview": "미리보기...",
      "created_at": "2026-01-09T..."
    }
  ]
}
```

#### 2. `POST /api/v1/save-summary/`
**수동 저장 API**

**요청**:
```json
{
  "title": "제목",
  "category": "하이노워킹",
  "content": "내용",
  "collection": "hino_draft | hino_final",
  "original_message": "원본 질문",
  "ai_response": { AI 응답 JSON }
}
```

#### 3. `POST /api/v1/generate-final/`
**최종본 생성 API** (선택된 문서들 종합)

**요청**:
```json
{
  "documents": [
    {"collection": "hino_draft", "doc_id": "abc123"},
    {"collection": "hino_draft", "doc_id": "def456"}
  ]
}
```

#### 4. `GET /api/v1/get-document/`
**개별 문서 조회**

**쿼리 파라미터**:
- `collection` - 컬렉션 이름
- `doc_id` - 문서 ID

#### 5. `POST /api/v1/update-documents/`
**여러 문서 일괄 수정**

**요청**:
```json
{
  "documents": [
    {"collection": "hino_draft", "doc_id": "abc123"}
  ],
  "updates": {
    "제목": "새 제목",
    "카테고리": "하이노워킹",
    "데이터상태": "FINAL"
  }
}
```

#### 6. `POST /api/v1/delete-documents/`
**여러 문서 일괄 삭제**

**요청**:
```json
{
  "documents": [
    {"collection": "hino_draft", "doc_id": "abc123"}
  ]
}
```

### 기타 API

- `GET /` - API 정보
- `GET /api/test/` - Firebase 연결 테스트
- `GET /api/logs/` - system_logs 조회
- `GET /chat/` - 웹 채팅 UI (템플릿)

---

## ⚙️ 환경 변수 (.env)

**파일**: `backend/.env`

```env
FIREBASE_CREDENTIALS_PATH=jnext-service-account.json
GEMINI_API_KEY=AIza...
JNEXT_API_KEY=(선택) API 인증 키
```

**중요**: `.env`와 `jnext-service-account.json`은 Git에 커밋 금지 (.gitignore에 등록됨)

---

## 🔄 데이터 흐름 예시

### 예시 1: 자연어 저장

**J님 입력**: "하이노워킹 기본동작 정리했어. 저장해줘"

**시스템 처리**:
1. `classify_intent()` → SAVE 의도 감지
2. `last_ai_response` (세션에 저장된 마지막 AI 답변) 확인
3. Gemini에게 출판용 전체 글 생성 요청
4. Firestore `hino_draft`에 문서 저장:
   - `내용` = 요약본
   - `전체글` = 출판용 전체 글 (1000-2000자)
5. 응답: "✅ hino_draft에 자동 저장되었습니다!"

---

### 예시 2: 자연어 검색

**J님 입력**: "하이노워킹 관련 문서 보여줘"

**시스템 처리**:
1. `classify_intent()` → READ 의도 감지
2. 카테고리 = "하이노워킹" 추출
3. Firestore 3단계 컬렉션 조회
4. 카테고리 필터링
5. `document_list` 생성 (체크박스 UI용)
6. 응답: "✅ 5개 문서를 찾았습니다" + 문서 목록

---

### 예시 3: 최종본 생성 (자연어)

**J님 입력**: "하이노워킹 기본 패스트 슬로우 종합해서 최종본 만들어"

**시스템 처리**:
1. `classify_intent()` → GENERATE_FINAL 의도 감지
2. 파라미터 추출:
   - `category` = "하이노워킹"
   - `include_keywords` = ["기본", "패스트", "슬로우"]
3. `hino_draft`와 `hino_raw`에서 조건 맞는 문서 검색
4. Gemini에게 종합 요청 (2000-5000자 완성본)
5. `hino_final`에 최종본 저장
6. 응답: "✅ 3개 문서를 종합하여 hino_final에 저장했습니다!"

---

## 🧠 핵심 코드 위치

### 1. AI 의도 분류

**파일**: `backend/api/ai_service.py`

```python
def classify_intent(user_message):
    """
    사용자 메시지에서 의도(Intent) 감지
    Returns: {
        'intent': 'SAVE | READ | UPDATE | DELETE | GENERATE_FINAL | NONE',
        'confidence': 0.0~1.0,
        'params': {...}
    }
    """
    # 키워드 기반 의도 분류
    # SAVE, READ, DELETE, UPDATE, GENERATE_FINAL, NONE
```

### 2. AI 모델 호출

**파일**: `backend/api/ai_service.py`

```python
def call_ai_model(model_name, user_message, system_prompt, db_context):
    """
    Gemini API 호출 (JSON 응답 강제)
    """
    # Gemini 2.5 Flash 사용
    # response_mime_type='application/json'
    # response_schema=AI_RESPONSE_SCHEMA
```

### 3. 메인 채팅 API

**파일**: `backend/api/views.py`

```python
@csrf_exempt
def chat(request):
    """
    [POST] /api/v1/chat/
    Phase 6: 통합 자연어 CRUD API
    """
    # 1. 의도 분류
    intent_data = classify_intent(user_message)
    
    # 2. 의도별 처리
    if intent == 'SAVE':
        # 자동 저장 로직
    elif intent == 'READ':
        # 검색 로직
    elif intent == 'GENERATE_FINAL':
        # 최종본 생성 로직
    else:
        # AI 대화 로직
```

### 4. Firestore 데이터 조회

**파일**: `backend/api/views.py`

```python
def search_firestore(collections=None, limit=50):
    """
    Firestore 데이터 조회 함수
    collections: None이면 3단계 모두 조회
    """
    # hino_raw, hino_draft, hino_final 조회
```

---

## 📱 모바일 앱 (Flutter)

### 메인 위젯

**파일**: `jnext_mobile/lib/main.dart`

```dart
class ChatScreen extends StatefulWidget {
  // 채팅 화면
  // API: http://192.168.219.139:8000/api/v1/chat/
}

class SearchScreen extends StatefulWidget {
  // 문서 검색 화면
}

class ChatBubble extends StatelessWidget {
  // 채팅 말풍선
  // document_list 표시
}
```

### API 호출

```dart
final response = await http.post(
  Uri.parse('http://192.168.219.139:8000/api/v1/chat/'),
  headers: {'Content-Type': 'application/json'},
  body: jsonEncode({'message': message, 'mode': 'organize'}),
);
```

---

## 🚨 중요 원칙

### 현재 단계: 검증·테스트

✅ **하면 되는 것**:
- 기존 기능 테스트
- 버그 수정
- 문서 정리
- 백업

❌ **하면 안 되는 것**:
- 새 기능 추가
- 필드 구조 변경
- 컬렉션 구조 변경
- 대규모 리팩토링

### 데이터 원칙

- **하이노밸런스만 대상**
- **필드 구조는 기존 정본에 종속**
- **추측하거나 새로 만들지 않음**

---

## 🛠️ 유지보수 정보

### Django 서버 재시작

```powershell
cd C:\Projects\JNext\backend
.\venv\Scripts\Activate.ps1
python manage.py runserver
```

### Firebase 연결 테스트

```
브라우저: http://localhost:8000/api/test/
```

### Gemini API 키 확인

```powershell
# .env 파일 확인
cat .env
```

### 로그 확인

```
브라우저: http://localhost:8000/api/logs/
```

---

## 📊 통계 (2026-01-09 기준)

- **백엔드 코드**: 약 2,000줄 (views.py + ai_service.py + settings.py)
- **모바일 코드**: 약 650줄 (main.dart)
- **지원 언어**: Python 3.14, Dart/Flutter
- **AI 모델**: Gemini 2.5 Flash
- **DB**: Firebase Firestore (NoSQL)

---

## 🎯 다음 할 일 (메모용)

- [ ] 웹 + 모바일 모두 테스트
- [ ] 자연어 의도 분류 정확도 확인
- [ ] SAVE 기능 테스트
- [ ] READ 기능 테스트
- [ ] GENERATE_FINAL 기능 테스트
- [ ] 오류 처리 강화

---

## 📝 메모

- J님을 "클로"로 호칭
- VS Code 재시작 시 이 문서 참고
- 백업 자주 하기

---

**문서 끝** - 다음 백업: 주요 변경 후
