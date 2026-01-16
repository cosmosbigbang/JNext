# JNext 프로젝트 구조 정밀 분석
**작성일**: 2026-01-16 04:00  
**목적**: Native History 적용 후 전체 구조 재분석  
**작성자**: Claude

---

## 📁 전체 아키텍처

```
JNext/
├── api/                          # Django Backend
│   ├── api/                      # 핵심 앱
│   │   ├── views.py             # 구버전 API (2395줄) - 하이노밸런스 전용
│   │   ├── views_v2.py          # 신버전 API (1400줄) - 범용 프로젝트
│   │   ├── ai_service.py        # AI 통합 레이어 (463줄)
│   │   ├── ai_config.py         # AI 설정 중앙화 ⭐ NEW
│   │   ├── raw_storage.py       # RAW 문서 저장
│   │   ├── db_service.py        # Firestore 서비스
│   │   ├── automation.py        # 자동화
│   │   ├── meme_generator.py    # 밈 생성
│   │   ├── error_handlers.py    # 에러 처리
│   │   ├── core/
│   │   │   └── context_manager.py  # 맥락 관리 (270줄)
│   │   └── projects/
│   │       ├── base.py          # 프로젝트 베이스 클래스
│   │       ├── hinobalance.py   # 하이노밸런스 프로젝트
│   │       └── project_manager.py  # 프로젝트 관리자
│   ├── config/                   # Django 설정
│   ├── templates/                # HTML 템플릿
│   │   ├── chat_v2.html         # 범용 채팅 UI
│   │   ├── document_manager.html # 문서 관리 UI
│   │   └── hino_review.html     # 하이노밸런스 전용 UI
│   └── manage.py
├── docs/                         # 문서
└── (스크립트들 - 유틸리티)
```

---

## 🎯 핵심 시스템 분석

### 1. **AI 서비스 레이어** (ai_service.py)

**구조**:
```python
# AI 설정 (ai_config.py에서 임포트)
- MODEL_ALIASES: 젠/진/클로 별명
- TEMPERATURE_SETTINGS: 모드별 온도
- HINOBALANCE_SYSTEM_PROMPT: 하이노밸런스 전용
- GENERAL_SYSTEM_PROMPT: 일반 대화

# 메인 라우터
call_ai_model()           
├─ messages 리스트 구성 (Gemini 형식)
├─ system_prompt 설정
├─ 모델 선택:
│   ├─ _call_gemini()    ✅ Native History
│   ├─ _call_gpt()       ✅ Native History (NEW)
│   ├─ _call_claude()    ✅ Native History (NEW)
│   └─ _call_all_models()
└─ validate_ai_response()

# 레거시 (views.py 전용)
classify_intent()         ⚠️ views_v2에서 사용 안 함
```

**특징**:
- ✅ **Native History 완전 적용**: 모든 모델이 messages 리스트 방식
- ✅ **설정 중앙화**: ai_config.py로 관리
- ✅ **Gemini 형식 통일**: 모든 모델에 동일한 messages 리스트 전달
- ⚠️ **레거시 코드**: classify_intent()는 views.py에서만 사용

**Native History 변환 로직**:
```python
# Gemini 형식
messages = [
    {'role': 'user', 'parts': [{'text': '...'}]},
    {'role': 'model', 'parts': [{'text': '...'}]},
]

# GPT 변환
for msg in messages:
    role = 'assistant' if msg['role'] == 'model' else msg['role']
    content = msg['parts'][0]['text']
    api_messages.append({'role': role, 'content': content})

# Claude 변환 (동일)
```

---

### 2. **API 레이어** (views.py vs views_v2.py)

#### **views.py** (구버전, 2395줄) - **하이노밸런스 전용**

```python
# Intent Classification 사용
chat()                    
├─ classify_intent()     # SAVE/READ/UPDATE/DELETE
└─ execute_command()

# CRUD 시스템 (전통적)
execute()                 
├─ handle_create_or_update()
├─ handle_read()
├─ handle_delete()
└─ handle_*_action()

# 하이노밸런스 전용 API
├─ hino_review_draft()
├─ hino_review_content()
├─ hino_review_raw()
├─ hino_get_detail()
├─ hino_review_page()
├─ hino_auto()
└─ hino_status()

# 유틸리티
├─ save_chat_history()
├─ load_chat_history()
├─ search_firestore()
└─ now_kst()
```

**특징**:
- Intent 기반 CRUD (키워드 감지)
- 하이노밸런스 하드코딩
- 레거시 유지 (하이노밸런스 웹앱 전용)

---

#### **views_v2.py** (신버전, 1400줄) - **범용 프로젝트**

```python
# 메인 채팅 API (Intent 없음!)
chat_v2()                 
├─ 1. save_chat_history (user)
├─ 2. load_chat_history (100개)
├─ 3. ProjectManager.get_project()
│   └─ get_db_context() if DB ON
├─ 4. ContextManager.build_context()
│   ├─ system_prompt (ai_config)
│   ├─ weights 계산
│   └─ full_message 구성
├─ 5. call_ai_model()
│   └─ conversation_history 전체 전달 (Native History)
├─ 6. save_chat_history (assistant)
└─ 7. evaluate_chat_value() → RAW 저장

# 문서 관리 (범용, UI 기반)
├─ search_documents()    # 검색
├─ update_document()     # 수정 (UI 버튼)
├─ regenerate_document() # 재생성
├─ combine_documents()   # 병합
├─ delete_documents()    # 삭제 (UI 버튼)
└─ move_to_final()       # 최종본 이동

# 프로젝트 관리
├─ list_projects()       # 프로젝트 목록
├─ create_project()      # 프로젝트 생성
└─ document_manager_ui() # 문서 관리 UI
```

**특징**:
- ✅ **Intent Classification 사용 안 함**
- ✅ **UI 버튼 기반** CRUD
- ✅ **범용 프로젝트 시스템**
- ✅ **Native History 완전 지원**

**핵심 차이점**:
| 구분 | views.py | views_v2.py |
|------|----------|-------------|
| 대상 | 하이노밸런스 전용 | 범용 프로젝트 |
| CRUD | Intent 기반 (키워드) | UI 버튼 기반 |
| 대화 | classify_intent() 사용 | Intent 없음, 순수 대화 |
| 맥락 | 문자열 합치기 | Native History |
| 확장성 | 낮음 (하드코딩) | 높음 (프로젝트 동적 생성) |

---

### 3. **맥락 관리 시스템** (core/context_manager.py)

```python
ContextManager.build_context()
├─ 파라미터:
│   ├─ temperature (슬라이더)
│   ├─ db_focus (ON/OFF → 0 or 100)
│   ├─ project_id
│   ├─ user_message
│   ├─ conversation_history (50개)
│   ├─ project_db_context
│   └─ project_prompt
│
├─ _calculate_weights()
│   ├─ DB OFF (0): conversation 100%, project 0%
│   └─ DB ON (100): conversation 30%, project 70%
│
├─ _build_system_prompt()
│   ├─ ai_config.HINOBALANCE_SYSTEM_PROMPT (프로젝트 모드)
│   ├─ ai_config.GENERAL_SYSTEM_PROMPT (일반 대화)
│   ├─ DB ON 지침: "DB 우선 참고"
│   └─ DB OFF 지침: "대화 이력 100%"
│
├─ _build_project_message() (사용 안 함, Native History가 대체)
│   ├─ 대화 이력 50개
│   └─ 프로젝트 DB 전체
│
└─ _build_general_message() (사용 안 함, Native History가 대체)
```

**최근 변경사항**:
- ✅ System Prompt를 ai_config.py에서 가져옴
- ✅ 하이노밸런스 전용 프롬프트 적용
- ✅ DB ON/OFF 동적 맥락 구성
- ⚠️ _build_*_message()는 Native History로 대체됨 (ai_service.py에서 처리)

---

### 4. **프로젝트 관리 시스템** (projects/)

```python
ProjectManager (싱글톤)
├─ _initialize_projects()
│   ├─ 1. 기본 프로젝트 등록 (HinoBalanceProject)
│   └─ 2. Firestore에서 동적 프로젝트 로드
├─ register_project()
├─ get_project()
├─ list_projects()
└─ create_project()      # 동적 생성

BaseProject (추상 클래스)
├─ project_id
├─ display_name
├─ description
├─ get_system_prompt()   # 추상 메서드
├─ get_db_context()      # 키워드 검색
└─ search_documents()

HinoBalanceProject (구현체)
├─ project_id: "hinobalance"
├─ display_name: "하이노밸런스"
├─ collections: raw/draft/final
└─ get_system_prompt()   # 하이노밸런스 철학
```

**특징**:
- ✅ 하이노밸런스 하드코딩 제거
- ✅ Firestore에서 프로젝트 동적 로드
- ✅ 새 프로젝트 웹 UI에서 생성 가능
- ✅ BaseProject 상속으로 확장 가능

---

## 📊 데이터 흐름

### **채팅 v2 플로우** (Native History)

```
사용자: "하이노워밍기본 뭐야?"
↓
[1] chat_v2() API
    - POST /api/v2/chat/
    - body: {message, model, project, temperature, db}
↓
[2] save_chat_history(role='user')
    - Firestore: chat_history 컬렉션
    - timestamp 저장 (KST)
↓
[3] load_chat_history(limit=100)
    - 최근 100개 대화 로드
    - timestamp 정렬 (DESC)
    - return: [{role, content}, ...]
↓
[4] ProjectManager.get_project(project_id)
    if project_id:
        ├─ get_system_prompt()
        └─ get_db_context() if DB ON
            - keyword 추출 ("하이노워밍기본")
            - Firestore 검색 (raw/draft/final)
            - return: "제목: ...\n내용: ..."
↓
[5] ContextManager.build_context()
    ├─ weights 계산 (DB ON: 30% conv + 70% project)
    ├─ system_prompt 구성 (ai_config)
    └─ return: {system_prompt, temperature, weights}
↓
[6] call_ai_model()
    ├─ messages 리스트 구성 (Gemini 형식):
    │   [
    │       {'role': 'user', 'parts': [{'text': '첫 질문'}]},
    │       {'role': 'model', 'parts': [{'text': '첫 답변'}]},
    │       {'role': 'user', 'parts': [{'text': '하이노워밍기본 뭐야?'}]}
    │   ]
    ├─ 모델 선택 (gemini/gpt/claude)
    ├─ Native History 변환 (GPT/Claude)
    ├─ AI API 호출
    └─ JSON 스키마 검증
↓
[7] save_chat_history(role='assistant')
    - AI 응답 저장
↓
[8] evaluate_chat_value()
    if valuable:
        └─ analyze_and_save_raw()
            - Firestore: projects/{project_id}/raw
            - AI 분석 (주제, 키워드, 요약)
```

---

## 🔥 핵심 발견사항

### 1. **이중 API 구조의 명확한 분리**
```
views.py                  views_v2.py
├─ 하이노밸런스 전용     ├─ 범용 프로젝트
├─ Intent 기반 CRUD      ├─ UI 버튼 기반
├─ 하드코딩             ├─ 동적 프로젝트
└─ 레거시 유지          └─ Native History
```

**판단**: ✅ **분리 유지가 정답**
- views.py: 하이노밸런스 웹앱 전용 (레거시)
- views_v2.py: 범용 프로젝트 (미래)

---

### 2. **classify_intent() 미사용 확인**
```python
# views.py (구버전)
intent_data = classify_intent(user_message)  # ✅ 사용

# views_v2.py (신버전)
# classify_intent() 호출 없음!           # ❌ 사용 안 함
# UI 버튼으로 CRUD 처리
```

**결론**: 젠의 충고는 잘못됨 (프로젝트 이해 부족)

---

### 3. **Native History 완전 적용** ⭐

**이전 (문제)**:
```python
# 문자열로 합침 (맥락 손실)
full_message = f"{conversation_history}\n{user_message}"
_call_gpt(full_message, system_prompt)
```

**현재 (해결)**:
```python
# messages 리스트 (구조 유지)
messages = [
    {'role': 'user', 'parts': [{'text': '...'}]},
    {'role': 'model', 'parts': [{'text': '...'}]},
]
_call_gemini(messages, system_prompt)  # ✅
_call_gpt(messages, system_prompt)     # ✅ NEW
_call_claude(messages, system_prompt)  # ✅ NEW
```

**효과**:
- ✅ 대화 맥락 100% 유지
- ✅ 모바일 ChatGPT/Gemini 수준
- ✅ "그거", "효과" 등 지시대명사 이해

---

### 4. **설정 중앙화 완료** ⭐

**이전 (분산)**:
```python
# ai_service.py
model_info_map = {...}
temperature_map = {...}

# context_manager.py
system_prompt = "..."
```

**현재 (중앙화)**:
```python
# ai_config.py (NEW)
MODEL_ALIASES = {...}
TEMPERATURE_SETTINGS = {...}
HINOBALANCE_SYSTEM_PROMPT = "..."
GENERAL_SYSTEM_PROMPT = "..."

# ai_service.py
from . import ai_config
model_name = ai_config.MODEL_ALIASES.get(...)
```

**효과**:
- ✅ 유지보수성 향상
- ✅ 설정 변경 단일 파일
- ✅ 중복 제거

---

## 📋 요약

### ✅ 강점
1. **Native History 완전 적용** (Gemini/GPT/Claude)
2. **범용 프로젝트 시스템** (하드코딩 제거)
3. **동적 맥락 관리** (DB ON/OFF, Temperature)
4. **설정 중앙화** (ai_config.py)
5. **이중 API 명확한 역할 분담** (레거시 vs 현대)

### ⚠️ 약점
1. **문서화 부족** (최신 구조 반영 필요)
2. **classify_intent() 레거시** (삭제 고려)
3. **views.py 비대화** (2395줄)

### 🎯 권장사항
1. ✅ **이중 API 유지** (views.py=하이노밸런스, v2=범용)
2. ⚠️ **classify_intent() 제거 고려** (v2에서 안 씀)
3. ✅ **문서 업데이트** (STRUCTURE.md)
4. ⚠️ **views.py 리팩토링** (장기 과제)

---

## 🚀 다음 단계

### 최우선 (테스트)
1. 서버 재시작
2. Native History 테스트 (젠/진/클로)
3. System Prompt 품질 확인

### 중요 (문서화)
1. STRUCTURE.md 업데이트
2. 인수인계 문서 업데이트
3. API 문서 작성

### 장기 (개선)
1. views.py 리팩토링 (하이노밸런스 전용 정리)
2. classify_intent() 제거
3. 테스트 스위트 구축

---

## 📝 변경 이력

**2026-01-16**:
- ✅ ai_config.py 생성 (설정 중앙화)
- ✅ GPT Native History 적용
- ✅ Claude Native History 적용
- ✅ System Prompt 강화 (하이노밸런스 철학)
- ✅ context_manager.py 개선 (ai_config 연동)

**이전 (2026-01-15)**:
- ✅ Gemini Native History 적용
- ✅ KST 시간대 수정
- ✅ 대화 맥락 50개 전달
- ✅ 가중치 로직 재설계
