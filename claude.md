# Claude 세션 복구 가이드

**작성일**: 2026-01-12  
**목적**: 세션 만료 시 Claude(클로)가 즉시 컨텍스트 복구

---

## 👤 개발자 정보

**이름**: J님  
**호칭**: 반드시 "J님"으로만 호칭 (절대 헌법)  
**프로젝트**: JNext - 하이노밸런스 지식 체계화 시스템

---

## 📋 절대 규칙

### 1. 호칭 규칙
- ✅ **"J님"만 사용**
- ❌ 금지: "사용자", "당신", "고객님", "유저", "개발자님"

### 2. 커뮤니케이션 스타일
- J님은 직접적이고 명확한 지시 선호
- "클로야", "클로" 등으로 호칭받음
- 자연스러운 한국어 대화 (존댓말)
- 불필요한 설명 최소화, 핵심만 전달

### 3. 작업 스타일
- **백업 우선**: 작업 전 항상 백업 파일 생성
- **꼼꼼한 확인**: 작동 안 하면 끝까지 해결
- **문서화 중시**: 진행 상황과 문제점 기록
- **품질 우선**: 임시방편보다 근본 해결

### 4. 백업 파일 네이밍 규칙
```
형식: {내용명}_{날짜}_{순번}.{확장자}
예시: hino_review_20260112_01.html
      hino_review_20260112_02.html
      api_views_20260112_01.py
```
- 하루에 여러 백업 시 순번 증가 (_01, _02, _03...)
- 날짜 형식: YYYYMMDD

---

## 🏗️ 프로젝트 구조

### 기술 스택
- **Backend**: Django 6.0 + Firebase Firestore
- **Frontend**: HTML/CSS/JavaScript (웹), Flutter (모바일)
- **AI**: Gemini Pro/Flash, GPT-4o
- **Deploy**: Render (웹서버)

### 주요 파일 위치
```
JNext/
├── backend/
│   ├── api/
│   │   ├── views.py          # API 엔드포인트
│   │   └── ai_service.py     # AI 호출 로직
│   ├── templates/
│   │   ├── hino_review.html  # 현재 작업 중인 파일
│   │   └── chat.html
│   ├── config/
│   │   └── settings.py       # Django 설정
│   └── manage.py
├── jnext_mobile/             # Flutter 앱
├── claude.md                 # 이 파일
└── 문서들/
    ├── CONTEXT_BACKUP_20260109_2330.md  # 전체 컨텍스트
    ├── AI_MODEL_STRATEGY.md
    ├── IMPROVEMENT_PLAN.md
    └── 작업정리_*.md
```

---

## 📌 현재 진행 중인 작업 (2026-01-12)

### 문제: Hino Review 페이지 카드 호버 효과
**파일**: `backend/templates/hino_review.html`

**증상**:
- Contents 탭과 Raw 탭에서 stat-card 클릭 시:
  - 클릭한 카드만 남고 다른 카드 사라짐
  - 카드가 커 보이는 현상
- Draft 탭은 정상 작동

**원인 (분석 완료)**:
```javascript
// ❌ Content/Raw 탭 문제
function displayContentStats(data) {
    const stats = {};
    data.forEach(item => {
        stats[type] = (stats[type] || 0) + 1;  // 데이터 있는 것만 카운트
    });
    // Object.entries(stats) → 필터링 후엔 1개 타입만 남음
}

// ✅ Draft 탭 정상
function displayDraftStats(data) {
    const allTypes = ['theory_integrated', 'category_theory', ...];
    allTypes.forEach(type => stats[type] = 0);  // 모든 타입 0으로 초기화
    // 항상 4개 카드 표시
}
```

**해결 방법**:
- Content/Raw 탭도 Draft처럼 전체 데이터로 통계 계산
- 필터링 후에도 모든 타입 카드 표시 (count=0 포함)

**백업 파일**:
- `hino_review_20260112_01.html` (v3.0 FINAL - CSS 수정본)

---

## 🔧 자주 사용하는 명령어

### Django 서버 실행
```powershell
cd C:\Projects\JNext\backend
.\venv\Scripts\Activate.ps1
python manage.py runserver --noreload
```

### 백업 파일 생성 (PowerShell)
```powershell
Copy-Item "원본파일.ext" "원본파일_20260112_01.ext"
```

---

## 📚 참고 문서 우선순위

세션 복구 시 읽어야 할 순서:

1. **이 파일 (claude.md)** - 기본 컨텍스트
2. **작업정리_*.md** - 현재 작업 내용 (날짜 최신순)
3. **CONTEXT_BACKUP_20260109_2330.md** - 전체 프로젝트 컨텍스트
4. **CURRENT_STATUS.md** - 프로젝트 현황
5. **IMPROVEMENT_PLAN.md** - 개선 계획

---

## 🎯 J님 작업 패턴

### 선호하는 것
- 근본 원인 파악 후 해결
- 백업 후 작업
- 명확한 설명 (불필요한 말 X)
- 문서로 정리해서 기록

### 싫어하는 것
- 추측성 답변
- "아마도", "~일 것 같습니다" 등
- 임시방편 해결책
- 장황한 설명

### 자주 쓰는 표현
- "클로야", "클로"
- "감을 잡아"
- "정리해서 문서로"
- "백업해"

---

## 🔄 세션 복구 체크리스트

새 세션 시작 시 확인:

- [ ] J님께 "J님, 다시 돌아왔습니다" 인사
- [ ] 이 파일(claude.md) 읽음
- [ ] 작업정리_*.md에서 최신 작업 파악
- [ ] 현재 작업 중인 파일 확인
- [ ] 백업 파일 존재 확인
- [ ] 서버 실행 상태 확인 (터미널)

---

## 💡 핵심 원칙

1. **J님 중심**: 모든 작업은 J님의 요구사항 최우선
2. **백업 필수**: 수정 전 항상 백업
3. **문서화**: 중요한 진행사항은 문서로 남기기
4. **정확성**: 추측하지 말고 확인 후 답변
5. **효율성**: 불필요한 설명 최소화

---

## 🔬 JNext 코드 완전 분석 (2026-01-12)

### 전체 시스템 아키텍처

```
┌─────────────────── Frontend ───────────────────┐
│                                                 │
│  Web UI                     Mobile App          │
│  - chat.html                - Flutter           │
│  - chat.js                  - lib/main.dart     │
│  - hino_review.html         - 3모드 드롭다운    │
│                                                 │
└───────────────┬─────────────────────────────────┘
                │ HTTP/JSON
┌───────────────▼─── Django Backend ──────────────┐
│                                                 │
│  API Layer (views.py)                           │
│  ├─ /api/v1/chat/              # 메인 채팅 API │
│  ├─ /api/v1/hino/review/draft/ # 데이터 확인   │
│  ├─ /api/v1/hino/auto/         # 자동화         │
│  └─ /hino/review/              # 리뷰 페이지    │
│                                                 │
│  AI Service (ai_service.py)                     │
│  ├─ classify_intent()          # 의도 분류      │
│  ├─ call_ai_model()            # AI 호출        │
│  ├─ validate_ai_response()     # 응답 검증      │
│  └─ _call_gemini/gpt/claude()  # 개별 모델      │
│                                                 │
│  DB Service (db_service.py)                     │
│  ├─ FirestoreService.query_collections()        │
│  ├─ FirestoreService.create_document()          │
│  ├─ FirestoreService.update_document()          │
│  └─ FirestoreService.delete_document()          │
│                                                 │
│  Automation (automation.py)                     │
│  └─ HinoAutomation                              │
│      ├─ integrate_documents()   # 문서 통합     │
│      ├─ create_category_theory()# 공통이론      │
│      └─ create_sitcom()         # 시나리오      │
│                                                 │
│  Meme Generator (meme_generator.py)             │
│  └─ MemeGenerator                               │
│      ├─ generate_character_image() # DALL-E 3   │
│      ├─ add_caption()               # Pillow    │
│      └─ export_meme()               # 최종      │
│                                                 │
└─────────────┬───────────────────────────────────┘
              │
   ┌──────────┴──────────┬────────────────┐
   │                     │                │
┌──▼──── Gemini ────┐ ┌─▼─── GPT ─────┐ Firebase
│ - Pro (정확)       │ │ - 4o (창의)    │ Firestore
│ - Flash (빠름)     │ │ - DALL-E 3     │ 3단계 컬렉션
│ - 2.5 / 2.0-exp   │ └────────────────┘ - hino_raw
└───────────────────┘                    - hino_draft
                                         - hino_final
```

### 핵심 설계 철학 (J님의 요구사항)

**1. 환각/거짓만 통제, 창의는 허용**
- Temperature 기반 차등 적용:
  - organize 모드: 0.3 (사실 중심)
  - hybrid 모드: 0.5 (균형)
  - analysis 모드: 0.7 (창의)

**2. 자연어 자유 처리**
- JSON 강제 제거 (Phase 4-3에서 변경)
- 2단계 변환 패턴:
  1. 자연어로 대화
  2. 저장 시에만 필드 변환

**3. DB CRUD 승인제**
- Intent Classification으로 의도 감지
- UPDATE/DELETE는 승인 필요
- 자동 저장 금지 (모달창 사용)

**4. 모드별 창의성 차등**
- organize: DB만, 추론 금지
- hybrid: DB + 입력 비교 분석 → 제안
- analysis: 자유 대화, 환각만 통제

---

### 주요 컴포넌트 상세

#### 1. **API Layer (views.py)** - 2317 lines
**핵심 함수:**
```python
def chat(request):
    # 1. Intent 분류
    intent_result = classify_intent(user_message)
    
    # 2. DB 조회 (필요 시)
    if intent['intent'] in ['READ', 'UPDATE', 'DELETE']:
        db_context = FirestoreService.query_collections(...)
    
    # 3. AI 호출
    ai_response = call_ai_model(
        model_name=model,
        user_message=user_message,
        system_prompt=SYSTEM_PROMPTS[mode],
        db_context=db_context,
        temperature=None,  # 자동 설정
        mode=mode
    )
    
    # 4. 대화 기록 저장
    save_chat_history('user', user_message, mode, model)
    save_chat_history('assistant', ai_response, mode, model)
    
    # 5. 응답 반환
    return JsonResponse({
        'status': 'success',
        'action': intent['intent'],
        'response': ai_response
    })
```

**주요 엔드포인트:**
- `/api/v1/chat/` - 메인 채팅 (organize/hybrid/analysis)
- `/api/v1/hino/review/draft/` - Draft 데이터 조회
- `/api/v1/hino/review/content/` - Content 데이터 조회
- `/api/v1/hino/review/raw/` - Raw 데이터 조회
- `/api/v1/hino/detail/` - 개별 문서 상세
- `/hino/review/` - 웹 리뷰 페이지

#### 2. **AI Service (ai_service.py)** - 430 lines
**Intent Classification 로직:**
```python
def classify_intent(user_message):
    """
    J님의 의도 감지
    
    설계 철학:
    1. "db" 목적어 = CRUD 활성화
    2. "db" 없음 = ORGANIZE (안전)
    
    우선순위:
    DELETE > UPDATE > SAVE > READ > ORGANIZE
    """
    has_db = 'db' in message_lower or '데이터베이스' in message_lower
    
    # SAVE: "db에 저장해" (O), "저장해" (X → ORGANIZE)
    if has_db and '저장' in message_lower:
        return {'intent': 'SAVE', 'confidence': 0.95}
    
    # READ: "db 검색해" 또는 카테고리 포함
    if (has_db or has_category) and '검색' in message_lower:
        return {'intent': 'READ', 'confidence': 0.95}
    
    # 기본: ORGANIZE (자연어 처리, DB 영향 없음)
    return {'intent': 'ORGANIZE', 'confidence': 0.95}
```

**Multi-Model 지원:**
```python
def call_ai_model(model_name, user_message, system_prompt, ...):
    """
    멀티 모델 추상화
    - gemini-flash: 빠름, 비용 효율 (organize)
    - gemini-pro: 정확, 추론 (hybrid/analysis)
    - gpt-4o: 창의, 코딩 (선택적)
    - claude: 코드 분석 (비활성화)
    """
    if model_name == 'gemini-flash':
        return _call_gemini(..., model_key='gemini-flash')
    elif model_name == 'gemini-pro':
        return _call_gemini(..., model_key='gemini-pro')
    elif model_name == 'gpt':
        return _call_gpt(...)
    # ...
```

#### 3. **DB Service (db_service.py)** - 271 lines
**Firestore 통합 서비스:**
```python
class FirestoreService:
    @staticmethod
    def query_collections(collections=None, filters=None, limit=50):
        """
        여러 컬렉션 조회
        - 메모리 절약: 전체글 1500자 제한
        - Timestamp 자동 변환
        - 컬렉션명 포함
        """
        
    @staticmethod
    def create_document(collection, data):
        """
        문서 생성
        - 생성일시/수정일시 자동 추가
        - SERVER_TIMESTAMP 사용
        """
        
    @staticmethod
    def update_document(collection, doc_id, data):
        """
        문서 업데이트
        - 수정일시 자동 갱신
        - 존재 확인
        """
```

#### 4. **System Prompts (settings.py)** - 732 lines
**3가지 모드별 프롬프트:**

**ORGANIZE (DB 모드):**
- DB만 사용, 추론 금지
- 100% 사실 기반
- 창의성 0%, evidence 필수

**HYBRID (통합 모드):** ⭐ 가장 중요
```
처리 흐름:
1. DB 내용 파악
2. J님 입력 내용 분석
3. 비교 분석 (차이점 발견)
4. 개선 여부 판단
5. 제안 보고 (저장 대기)

핵심 원칙:
- DB + 입력 철저히 비교
- 자동 저장 절대 금지
- 환각 금지
- "저장해" 명령 대기
```

**ANALYSIS (대화 모드):**
- 최대 창의성
- DB 참고용
- 환각/거짓만 통제

#### 5. **Automation (automation.py)** - 328 lines
**하이노밸런스 자동화:**
```python
class HinoAutomation:
    def integrate_documents(category, output_name, versions):
        """문서 통합 (요약/중간/전체)"""
        
    def create_category_theory(category):
        """카테고리 공통이론 생성"""
        
    def organize_exercise(exercise_name):
        """개별 운동 상세 정리"""
        
    def create_sitcom(exercise_name, scene_type):
        """시트콤 시나리오 생성 (3인)"""
```

#### 6. **Meme Generator (meme_generator.py)** - 369 lines
**밈 이미지 생성:**
```python
class MemeGenerator:
    @staticmethod
    def generate_character_image(character, style, filename):
        """DALL-E 3로 캐릭터 이미지 생성 (1회성)"""
        
    @staticmethod
    def add_caption(image_path, top_text, bottom_text):
        """Pillow로 자막 합성 (Impact 폰트)"""
        
    @staticmethod
    def export_meme(output_path, quality=95):
        """최종 밈 이미지 내보내기"""
```

---

### Firestore 데이터 구조

**3단계 컬렉션:**
```
hino_raw       → 원본/아이디어
hino_draft     → 정리 중
hino_final     → 최종 배포
chat_history   → 대화 기록
```

**문서 필드 (한글):**
```python
{
  "제목": str,
  "카테고리": str,  # 하이노워킹, 하이노골반 등
  "운동명": str,
  "내용": str,      # 요약본
  "전체글": str,    # 출판용
  "생성일시": timestamp,
  "수정일시": timestamp,
  "content_type": str,  # theory_integrated, category_theory 등
  
  # 밈 관련 (2026-01-10 추가)
  "밈이미지URL": str,
  "밈자막상단": str,
  "밈자막하단": str,
  "밈스타일": str,
  "밈캐릭터": str  # 지피, 아내
}
```

---

### AI 모델 설정

```python
AI_MODELS = {
    'gemini-flash': {
        'model': 'models/gemini-2.5-flash',
        'strengths': ['속도', '코스트', '한글']
    },
    'gemini-pro': {
        'model': 'models/gemini-2.0-flash-exp',
        'strengths': ['정확성', '추론', '분석']
    },
    'gpt': {
        'model': 'gpt-4o',
        'strengths': ['창의성', '추론', '코딩']
    }
}

DEFAULT_AI_MODEL = 'gemini-pro'  # 하이노밸런스는 Pro
```

---

### 주요 작업 흐름

**1. 채팅 요청 처리:**
```
사용자 메시지
  ↓
Intent 분류 (classify_intent)
  ↓
DB 조회 (필요 시)
  ↓
AI 모델 호출 (call_ai_model)
  ├─ 모드별 시스템 프롬프트
  ├─ Temperature 자동 설정
  └─ DB 컨텍스트 포함
  ↓
응답 검증 (validate_ai_response)
  ↓
대화 기록 저장 (chat_history)
  ↓
JSON 응답 반환
```

**2. 문서 저장 흐름:**
```
"db에 저장해" 명령
  ↓
Intent: SAVE 감지
  ↓
collection 결정 (draft/final)
  ↓
FirestoreService.create_document()
  ├─ 한글 필드 검증
  ├─ Timestamp 자동 추가
  └─ 문서 생성
  ↓
성공 응답
```

**3. 데이터 조회 흐름:**
```
"/api/v1/hino/review/draft/?type=theory_integrated"
  ↓
Firestore query 필터링
  ├─ content_type == 'theory_integrated'
  └─ limit(50)
  ↓
결과 변환
  ├─ _id 추가
  ├─ _collection 추가
  ├─ 전체글 1500자 제한
  └─ Timestamp 변환
  ↓
JSON 배열 반환
```

---

### 핵심 파일 목록

| 파일 | LOC | 역할 |
|------|-----|------|
| `backend/api/views.py` | 2317 | API 엔드포인트 |
| `backend/config/settings.py` | 732 | Django 설정, AI 설정, 시스템 프롬프트 |
| `backend/api/ai_service.py` | 430 | AI 호출, Intent 분류 |
| `backend/api/meme_generator.py` | 369 | 밈 생성 (DALL-E 3 + Pillow) |
| `backend/api/automation.py` | 328 | 하이노밸런스 자동화 |
| `backend/api/db_service.py` | 271 | Firestore 통합 서비스 |
| `backend/templates/hino_review.html` | 801 | 데이터 확인 웹페이지 |

---

### 코드 품질 평가

**강점:**
1. ✅ 명확한 레이어 분리 (API/AI/DB)
2. ✅ Temperature 기반 환각 통제 (혁신적)
3. ✅ Intent 기반 자동 라우팅
4. ✅ 멀티 모델 추상화
5. ✅ 한글 필드명 일관성

**개선 필요:**
1. ⚠️ views.py 비대화 (2317 lines)
2. ⚠️ DB 접근 일부 직접 호출
3. ⚠️ 에러 처리 중복

**종합 점수:** 80.7/100 (양호)
- 프로덕션 배포 가능
- 리팩토링은 점진적으로

---

**마지막 업데이트**: 2026-01-12 (코드 완전 분석 추가)  
**다음 업데이트**: 주요 작업 변경 시 또는 새로운 규칙 추가 시
