# JNext AI 모델 전략

**작성일**: 2026-01-09  
**작성자**: J님 지시사항 기반 정리

---

## 📊 모델별 용도 구분

### 하이노밸런스 (JNext 프로젝트)
- **주력 모델**: Gemini Pro
- **보조 모델**: GPT-4o (진)
- **목적**: 정확한 분석, 고품질 최종본 생성, DB 통합 추론

### 모의고사 앱 (향후 프로젝트)
- **주력 모델**: Gemini Flash
- **목적**: 빠른 응답, 비용 효율, 대량 문제 처리

---

## 🔧 현재 상태

### ✅ 구현 완료
- Gemini Flash (2.5) 연동
- 멀티 모델 추상화 구조 (`ai_service.py`)
- 모델 설정 인프라 (`settings.py AI_MODELS`)

### ⚠️ 준비 필요
1. **Gemini Pro 추가**
   - 모델명: `models/gemini-2.0-flash-exp` 또는 `models/gemini-1.5-pro`
   - 설정 위치: `settings.py AI_MODELS['gemini-pro']`
   - 환경 변수: 동일 API 키 사용 가능

2. **GPT-4o 추가**
   - 모델명: `gpt-4o`
   - 라이브러리: `openai` 패키지 설치
   - 환경 변수: `OPENAI_API_KEY`
   - 구현 위치: `ai_service.py _call_gpt()`

3. **모드별 모델 자동 선택 로직**
   - `organize` 모드 → Flash (빠른 CRUD)
   - `hybrid` 모드 → **Pro** (통합 분석)
   - `analysis` 모드 → **Pro** 또는 GPT (심화 대화)

---

## 📝 구현 계획

### Phase 1: Gemini Pro 추가 (우선순위 높음)

#### 1.1 settings.py 수정
```python
AI_MODELS = {
    'gemini-flash': {
        'enabled': GEMINI_INITIALIZED,
        'model': 'models/gemini-2.5-flash',
        'client': GEMINI_CLIENT,
        'strengths': ['속도', '코스트', '한글'],
        'use_case': ['모의고사', 'CRUD', '빠른응답']
    },
    'gemini-pro': {
        'enabled': GEMINI_INITIALIZED,  # 동일 API 키
        'model': 'models/gemini-2.0-flash-exp',  # 또는 gemini-1.5-pro
        'client': GEMINI_CLIENT,
        'strengths': ['정확성', '추론', '분석'],
        'use_case': ['하이노밸런스', '최종본생성', '통합분석']
    },
    # ... GPT, Claude
}

# 하이노밸런스 기본 모델
DEFAULT_AI_MODEL = 'gemini-pro'  # Flash → Pro 변경
```

#### 1.2 ai_service.py 수정
```python
def _call_gemini(full_message, system_prompt, model_key='gemini-flash'):
    """
    model_key: 'gemini-flash' | 'gemini-pro'
    """
    if model_key not in settings.AI_MODELS:
        model_key = 'gemini-flash'  # fallback
    
    config = settings.AI_MODELS[model_key]
    if not config['enabled']:
        raise Exception(f"{model_key} not initialized")
    
    client = config['client']
    model = config['model']
    
    # ... 기존 로직
```

#### 1.3 views.py 모드별 모델 선택
```python
@csrf_exempt
def chat(request):
    # ...
    mode = data.get('mode', 'hybrid')
    
    # 모드별 모델 자동 선택
    if mode == 'organize':
        model_key = 'gemini-flash'  # 빠른 CRUD
    elif mode == 'hybrid':
        model_key = 'gemini-pro'    # 통합 분석 (Pro)
    elif mode == 'analysis':
        model_key = 'gemini-pro'    # 심화 대화 (Pro)
    
    # AI 호출
    ai_response = call_ai_model(
        model_name=model_key,
        user_message=user_message,
        system_prompt=system_prompt,
        db_context=db_context
    )
```

---

### Phase 2: GPT-4o 추가 (보조 모델)

#### 2.1 패키지 설치
```bash
pip install openai
```

#### 2.2 .env 환경 변수
```
OPENAI_API_KEY=sk-...
```

#### 2.3 settings.py 초기화
```python
import openai

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', None)
if OPENAI_API_KEY:
    GPT_CLIENT = openai.OpenAI(api_key=OPENAI_API_KEY)
    GPT_INITIALIZED = True
else:
    GPT_CLIENT = None
    GPT_INITIALIZED = False
```

#### 2.4 ai_service.py 구현
```python
def _call_gpt(full_message, system_prompt):
    """GPT-4o API 호출"""
    if not settings.AI_MODELS['gpt']['enabled']:
        raise Exception("GPT not initialized")
    
    client = settings.AI_MODELS['gpt']['client']
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": full_message}
            ],
            temperature=0.7,
            response_format={"type": "json_object"}  # JSON 강제
        )
        
        result = json.loads(response.choices[0].message.content)
        result['_model'] = 'gpt'
        return result
        
    except Exception as e:
        return {
            'answer': f'GPT 호출 실패: {str(e)}',
            'claims': [],
            'evidence': [],
            'confidence': 0.0,
            '_model': 'gpt',
            '_error': str(e)
        }
```

---

### Phase 3: 2두/3두 체계 (선택적)

#### 진(GPT) + 클로드(Gemini Pro) 동시 호출
```python
# views.py - 특정 케이스에서만 사용
if user_message.startswith('중요:'):
    # 2두 체계: Pro + GPT 동시 호출 후 비교
    model_key = 'all'
    ai_response = _call_all_models(full_message, system_prompt)
```

#### 응답 비교 UI (웹/모바일)
- Gemini Pro 응답
- GPT 응답
- J님이 선택하여 저장

---

## 🎯 단계별 실행 계획

### 즉시 실행 (새벽 테스트 전)
- [ ] settings.py에 `gemini-pro` 모델 추가
- [ ] DEFAULT_AI_MODEL을 `gemini-pro`로 변경
- [ ] ai_service.py에 model_key 파라미터 추가
- [ ] views.py 모드별 모델 선택 로직 추가
- [ ] requirements.txt는 변경 없음 (동일 google-genai 사용)

### 1주일 내 (안정화 후)
- [ ] openai 패키지 설치
- [ ] GPT_CLIENT 초기화
- [ ] _call_gpt() 구현
- [ ] 웹 UI에 모델 선택 드롭다운 추가 (Flash/Pro/GPT)

### 2주일 내 (고급 기능)
- [ ] 2두 체계 구현 (Pro + GPT 동시 호출)
- [ ] 응답 비교 UI
- [ ] 모델별 성능/비용 로깅

---

## 💰 비용 예상

### Gemini (Google)
- Flash: $0.075 / 1M tokens (입력), $0.30 / 1M tokens (출력)
- Pro: $1.25 / 1M tokens (입력), $5.00 / 1M tokens (출력)
- **예상**: 하이노밸런스 테스트 100회 → $0.50 ~ $1.00

### GPT-4o (OpenAI)
- $2.50 / 1M tokens (입력), $10.00 / 1M tokens (출력)
- **예상**: 보조 사용 시 월 $5 ~ $10

---

## 📌 주의사항

1. **Pro 모델은 느림**: Flash 대비 2~3배 느릴 수 있음
2. **CRUD는 Flash 유지**: 단순 저장/조회는 Flash로 충분
3. **최종본 생성만 Pro**: `GENERATE_FINAL` action일 때만 Pro 사용
4. **GPT는 선택적**: J님이 "진 불러"라고 하면 GPT 호출

---

**다음 단계**: J님 승인 후 즉시 실행 항목부터 구현
