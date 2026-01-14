# Gemini API 문제 - 진단 요청

## 문제 요약
Google GenAI SDK의 `generate_content()` 메서드 호출 시 계속 `400 INVALID_ARGUMENT` 에러 발생.
코드는 공식 문서대로 수정했으나 서버가 변경사항을 반영하지 못하는 것으로 추정.

## 에러 메시지
```
400 INVALID_ARGUMENT. {'error': {'code': 400, 'message': '* GenerateContentRequest.generation_config)
```

## 수정 내역

### 1. 올바른 API 사용법 확인
```python
# Python에서 시그니처 확인
from google.genai import types
import inspect

# GenerateContentConfig 파라미터
print(inspect.signature(types.GenerateContentConfig))
# 결과: systemInstruction, temperature, maxOutputTokens, responseMimeType, responseSchema 등
# ❗ camelCase 사용 (snake_case 아님)
```

### 2. 수정한 파일들

#### a) `backend/api/ai_service.py` (Line 260-275)
```python
# ❌ 기존 (잘못된 방식)
response = client.models.generate_content(
    model=model,
    contents=full_message,
    config={
        'system_instruction': system_prompt,  # snake_case
        'temperature': temperature,
        'max_output_tokens': 32768,
        'response_mime_type': 'application/json',
        'response_schema': settings.AI_RESPONSE_SCHEMA,
    }
)

# ✅ 수정 후 (올바른 방식)
from google.genai import types

response = client.models.generate_content(
    model=model,
    contents=full_message,
    config=types.GenerateContentConfig(  # 객체 사용
        systemInstruction=system_prompt,  # camelCase
        temperature=temperature,
        maxOutputTokens=32768,
        responseMimeType='application/json',
        responseSchema=settings.AI_RESPONSE_SCHEMA,
    )
)
```

#### b) `backend/api/raw_storage.py` (2곳)

**Line 55-65: evaluate_chat_value()**
```python
# ✅ 수정됨
from google.genai import types

response = client.models.generate_content(
    model=model,
    contents=prompt,
    config=types.GenerateContentConfig(
        temperature=0.2,
        maxOutputTokens=100,
    )
)
```

**Line 115-125: analyze_and_save_raw()**
```python
# ✅ 수정됨
from google.genai import types

response = client.models.generate_content(
    model=gemini_model,
    contents=analysis_prompt,
    config=types.GenerateContentConfig(
        temperature=0.3,
        maxOutputTokens=2048,
        responseMimeType='application/json'
    )
)
```

#### c) `backend/api/views.py` (2곳)

**Line 1075-1085: publish 기능**
```python
# ✅ 수정됨
from google.genai import types

publish_response = client.models.generate_content(
    model=model,
    contents=publish_prompt,
    config=types.GenerateContentConfig(temperature=0.8)
)
```

**Line 1480-1490: synthesis 기능**
```python
# ✅ 수정됨
from google.genai import types

synthesis_response = client.models.generate_content(
    model=model_name,
    contents=synthesis_prompt,
    config=types.GenerateContentConfig(temperature=0.7, responseMimeType='application/json')
)
```

## 검증 테스트

### 성공한 테스트
```python
# Django 설정 로드 후 직접 호출
from google.genai import types
config = types.GenerateContentConfig(temperature=0.5, maxOutputTokens=100)
response = settings.AI_MODELS['gemini-pro']['client'].models.generate_content(
    model='gemini-2.0-flash-exp', 
    contents='테스트', 
    config=config
)
print('✅ Gemini 성공:', response.text[:100])
# 결과: 정상 작동
```

### 실패하는 테스트
```bash
# HTTP API 호출
curl -X POST http://localhost:8000/api/v2/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message":"테스트","temperature":50,"db_focus":50,"model":"gemini-flash"}'

# 결과: 400 INVALID_ARGUMENT (generation_config 에러)
```

## 시도한 해결 방법

1. ✅ Git checkout으로 파일 복원 → 다시 수정
2. ✅ 서버 재시작 (Ctrl+C → python manage.py runserver)
3. ✅ 파일 재저장으로 StatReloader 트리거
4. ❌ 여전히 같은 에러 발생

## 의심 사항

### 1. 서버가 코드 변경을 반영하지 못함
- StatReloader가 작동하는데도 에러 메시지가 동일
- 파일은 수정되었으나 메모리에 로드된 코드는 이전 버전일 가능성
- Python import cache 문제?

### 2. 다른 곳에서 구식 config 사용 중
- `backend/api/` 외의 파일에서 Gemini 호출하는 곳 있음
- `automation.py`, `content_generator.py` 등은 아직 수정 안 함
- 하지만 `/api/v2/chat/` 엔드포인트는 `ai_service.py`만 사용

### 3. 환경 변수 문제
- Django settings 재로드 이슈?
- AI_MODELS 딕셔너리가 초기화 시점에만 생성되고 업데이트 안 됨?

## 환경 정보

- Python: 3.14
- Django: 6.0
- google-genai SDK: (버전 확인 필요)
- OS: Windows
- 서버: Django development server (runserver)

## 요청 사항

**이 문제의 원인을 진단해주세요:**

1. 코드는 올바르게 수정되었나요?
2. 서버가 변경사항을 반영하지 못하는 이유는?
3. 추가로 확인해야 할 파일이나 설정이 있나요?
4. Django StatReloader 말고 다른 재시작 방법이 필요한가요?

## 현재 파일 상태

```bash
# 파일 수정 확인
git status
# 결과: ai_service.py, raw_storage.py, views.py, project_manager.py, views_v2.py, urls.py 수정됨
```

## 추가 정보

- GPT 모델은 정상 작동
- Claude는 초기화 실패 (proxies 인자 에러, 비차단)
- Gemini 초기화는 성공 ("[JNext] Gemini AI initialized successfully")
- 문제는 `generate_content()` 호출 시에만 발생
