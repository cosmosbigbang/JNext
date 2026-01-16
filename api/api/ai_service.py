"""
AI 서비스 추상화 레이어
멀티 모델 지원 (Gemini, GPT, Claude)
Phase 6: 의도 분류 (Intent Classification)
Phase 7: JSON 스키마 검증
"""
from django.conf import settings
from google import genai
import json
import re
from . import ai_config


def validate_ai_response(response):
    """
    AI 응답 JSON 스키마 검증 및 보정
    
    Args:
        response: AI 모델의 응답 dict
    
    Returns:
        dict: 검증 및 보정된 응답
    """
    # 필수 필드 기본값
    defaults = {
        'answer': '',
        'claims': [],
        'evidence': [],
        'missing_info': [],
        'confidence': 0.5,
        'actions_suggested': []
    }
    
    # 누락된 필드 보정
    for field, default_value in defaults.items():
        if field not in response:
            response[field] = default_value
    
    # 타입 검증 및 보정
    if not isinstance(response['answer'], str):
        response['answer'] = str(response['answer'])
    
    if not isinstance(response['claims'], list):
        response['claims'] = []
    
    if not isinstance(response['evidence'], list):
        response['evidence'] = []
    
    if not isinstance(response['missing_info'], list):
        response['missing_info'] = []
    
    if not isinstance(response['confidence'], (int, float)):
        response['confidence'] = 0.5
    else:
        # confidence 범위 제한 (0~1)
        response['confidence'] = max(0.0, min(1.0, float(response['confidence'])))
    
    if not isinstance(response['actions_suggested'], list):
        response['actions_suggested'] = []
    
    return response


def classify_intent(user_message):
    """
    J님의 의도(Intent) 감지
    
    설계 철학 (J님):
    1. "db" 목적어 = CRUD 활성화
    2. "db" 없음 = ORGANIZE (안전)
    
    핵심:
    - "db 검색해" → READ (DB 조회)
    - "db 분석해" → ORGANIZE (DB 읽기만)
    - "db 수정해" → UPDATE (DB 수정)
    - "db 삭제해" → DELETE (DB 삭제)
    - "검색해" → ORGANIZE (자연어, DB 영향 없음)
    
    Returns:
        dict: {
            'intent': 'SAVE' | 'READ' | 'UPDATE' | 'DELETE' | 'ORGANIZE',
            'confidence': 0.95,
            'params': {...}
        }
    
    J님 설계 철학:
    - 명령어는 단순하게 (복합 명령어 없음)
    - 모든 저장은 모달창 (자동 저장 없음)
    - 자연어는 AI에게 맡김 (최대한 활용)
    - DB 통제만 엄격 (거짓/환각/메모리)
    """
    message = user_message.strip()
    message_lower = message.lower()
    
    # DB 목적어 체크 (CRUD 활성화)
    has_db = any(db in message_lower for db in ['db', 'database', '데이터베이스', '디비'])
    
    # SAVE (엄격: "db" 필수!)
    # ⚠️ J님 철학: "db" 목적어 없으면 모두 ORGANIZE
    #   - "db에 저장해" → SAVE (CRUD)
    #   - "저장해" → ORGANIZE (자연어, AI가 준비만 함)
    if has_db and any(cmd in message_lower for cmd in ['저장해', '저장해줘', '기록해', '보관해']):
        # 제외: "저장해서", "저장하고" 등
        if not any(exc in message_lower for exc in ['저장해서', '저장해도', '저장하고', '저장하면']):
            params = {
                'collection': 'final' if any(k in message_lower for k in ['최종', 'final', '완료']) else 'draft',
                'target': 'last_response'
            }
            return {
                'intent': 'SAVE',
                'confidence': 0.95,
                'params': params
            }
    
    # 카테고리 목록 (하이노밸런스 운동 순서)
    categories = ['하이노이론', '하이노워밍', '하이노골반', '하이노워킹', '하이노스케이팅', '하이노풋삽', '하이노철봉', '하이노기타']
    has_category = any(cat in message_lower for cat in categories)
    
    # DELETE (엄격: "db" 또는 카테고리 필수)
    # "db 삭제해" 또는 "하이노밸런스 삭제해" 모두 허용
    if (has_db or has_category) and any(cmd in message_lower for cmd in ['삭제해', '삭제해줘', '지워', '지워줘', '제거해']):
        if not any(exc in message_lower for exc in ['삭제해서', '삭제하고', '삭제하면']):
            return {
                'intent': 'DELETE',
                'confidence': 0.95,
                'params': {'requires_approval': True}
            }
    
    # UPDATE (엄격: "db" 필수 + 제외 조건)
    # ⚠️ 구분:
    #   - "db 수정해" → UPDATE (CRUD, 실제 DB 수정)
    #   - "수정해서 보여줘", "통합해" → ORGANIZE (자연어, DB 안 건드림)
    if has_db and any(cmd in message_lower for cmd in ['수정해', '수정해줘', '고쳐', '고쳐줘', '바꿔', '바꿔줘', '변경해']):
        # 제외: 자연어 명령 (AI가 수정안만 보여주기)
        if not any(exc in message_lower for exc in ['수정해서', '수정해도', '수정하고', '수정하면', '보여줘', '보여주', '통합']):
            return {
                'intent': 'UPDATE',
                'confidence': 0.95,
                'params': {'requires_approval': True}
            }
    
    # READ (엄격: "db" 또는 카테고리 필수)
    db_targets = categories + ['draft', '초안', 'final', '최종', 'raw', '원본', '하이노밸런스']
    
    has_category = any(cat in message_lower for cat in db_targets)
    
    if (has_db or has_category) and any(cmd in message_lower for cmd in ['검색해', '검색해줘', '찾아줘', '가져와', '가져와줘', '조회해', '보여줘', '보여주']):
        params = {'collections': []}
        
        # 컬렉션 필터링 (subcollection 이름만)
        if 'draft' in message_lower or '초안' in message_lower:
            params['collections'].append('draft')
        if 'final' in message_lower or '최종' in message_lower:
            params['collections'].append('final')
        if 'raw' in message_lower or '원본' in message_lower:
            params['collections'].append('raw')
        
        # 카테고리 필터링 (하이노밸런스 운동 순서)
        for category in categories:
            if category in message:
                params['category'] = category
                break
        
        return {
            'intent': 'READ',
            'confidence': 0.95,
            'params': params
        }
    
    # ORGANIZE (자연어 처리, DB 영향 없음)
    # "수정해서 보여달라" = AI가 수정안 생성 → 보여주기만
    return {
        'intent': 'ORGANIZE',
        'confidence': 0.95,
        'params': {}
    }


def call_ai_model(model_name, user_message, system_prompt, db_context, temperature=None, mode='hybrid', conversation_history=None):
    """
    AI 모델 호출 (멀티 모델 지원)
    
    Args:
        model_name: 'gemini-flash' | 'gemini-pro' | 'gpt' | 'claude' | 'all'
        user_message: J님의 메시지 (v2에서는 이미 맥락이 포함된 full_message)
        system_prompt: 시스템 프롬프트
        db_context: Firestore DB 데이터 (v2에서는 빈 문자열)
        temperature: 창의성 수준 (None이면 mode에 따라 자동 설정)
        mode: 'organize' | 'hybrid' | 'analysis' | 'v2'
        conversation_history: 이전 대화 기록 (v2에서는 빈 리스트)
    
    Returns:
        dict: JSON 응답 (AI_RESPONSE_SCHEMA 형식)
    """
    # Temperature 자동 설정 (ai_config에서 가져오기)
    if temperature is None:
        temperature = ai_config.TEMPERATURE_SETTINGS.get(mode, 0.5)
    
    # 모델 정보 주입 (ai_config에서 가져오기)
    model_name_korean = ai_config.MODEL_ALIASES.get(model_name, model_name)
    enhanced_prompt = f"🎯 당신의 이름: {model_name_korean}\n\n{system_prompt}"
    
    # Gemini Native History: 메시지 리스트 구성
    messages = []
    
    # 대화 이력을 리스트로 적재 (Native History)
    if conversation_history and len(conversation_history) > 0:
        for msg in conversation_history:
            # Gemini API: 'assistant' → 'model'
            role = 'model' if msg['role'] in ['assistant', 'model'] else 'user'
            messages.append({'role': role, 'parts': [{'text': msg['content']}]})
    
    # 현재 유저 메시지 추가
    messages.append({'role': 'user', 'parts': [{'text': user_message}]})
    
    # DB Context가 있으면 시스템 프롬프트에 추가
    final_system_prompt = enhanced_prompt
    if db_context:
        final_system_prompt += f"\n\n[참고할 DB 지식]\n{db_context}"
    
    # Gemini 계열 (Flash/Pro) - Native History 전달
    if model_name in ['gemini-flash', 'gemini-pro']:
        return _call_gemini(messages, final_system_prompt, model_key=model_name, temperature=temperature)
    
    # 기본값 fallback
    elif model_name == 'gemini' or not model_name:
        return _call_gemini(messages, final_system_prompt, model_key=settings.DEFAULT_AI_MODEL, temperature=temperature)
    
    elif model_name == 'gpt':
        # GPT Native History 적용
        return _call_gpt(messages, final_system_prompt, temperature=temperature)
    
    elif model_name == 'claude':
        # Claude Native History 적용
        return _call_claude(messages, final_system_prompt, temperature=temperature)
    
    elif model_name == 'all':
        # 멀티 모델은 문자열로 변환 필요 (향후 개선)
        full_message = messages[-1]['parts'][0]['text'] if mode == 'v2' else user_message
        return _call_all_models(full_message, system_prompt, temperature=temperature)
    
    else:
        raise ValueError(f"Unknown model: {model_name}")


def _call_gemini(messages, system_prompt, model_key='gemini-pro', temperature=0.5):
    """Gemini API 호출 (Native History 지원)
    
    Args:
        messages: [{'role': 'user'|'model', 'parts': [{'text': '...'}]}] 형태의 리스트
        system_prompt: 시스템 프롬프트
        model_key: 'gemini-flash' | 'gemini-pro'
        temperature: 창의성 수준 (0.0~1.0)
    """
    if model_key not in settings.AI_MODELS:
        model_key = 'gemini-pro'  # fallback
    
    if not settings.AI_MODELS[model_key]['enabled']:
        raise Exception(f"{model_key} not initialized")
    
    client = settings.AI_MODELS[model_key]['client']
    model = settings.AI_MODELS[model_key]['model']
    
    try:
        # Google GenAI SDK 호출
        from google.genai import types
        
        print("="*80)
        print(f"🔍 [DEBUG] _call_gemini 실행 시작")
        print(f"   model_key: {model_key}")
        print(f"   model: {model}")
        print(f"   temperature: {temperature}")
        print(f"   messages: {len(messages)} turns")
        print("="*80)
        
        response = client.models.generate_content(
            model=model,
            contents=messages,  # Native History: 리스트 전달
            config=types.GenerateContentConfig(
                systemInstruction=system_prompt,
                temperature=temperature,
                maxOutputTokens=32768,
                responseMimeType='application/json',
                responseSchema=settings.AI_RESPONSE_SCHEMA,
            )
        )
        
        print(f"✅ [DEBUG] Gemini 응답 성공")
        print("="*80)
        
        # JSON 파싱
        result = json.loads(response.text)
        result['_model'] = model_key
        result['_model_version'] = model
        
        # 스키마 검증
        return validate_ai_response(result)
        
    except json.JSONDecodeError as e:
        # JSON 파싱 실패 시 fallback
        return {
            'answer': response.text,
            'claims': [],
            'evidence': [],
            'missing_info': ['JSON 응답 파싱 실패'],
            'confidence': 0.5,
            'actions_suggested': [],
            '_model': model_key,
            '_error': str(e)
        }


def _call_gpt(messages, system_prompt, temperature=0.7):
    """GPT API 호출 (Native History 지원)"""
    if not settings.AI_MODELS['gpt']['enabled']:
        raise Exception("GPT not initialized")
    
    client = settings.GPT_CLIENT
    model = settings.AI_MODELS['gpt']['model']
    
    try:
        # 시스템 프롬프트를 메시지 리스트의 시작에 추가
        api_messages = [{"role": "system", "content": f"{system_prompt}\n\n반드시 다음 JSON 형식으로만 응답하세요:\n{json.dumps(settings.AI_RESPONSE_SCHEMA, ensure_ascii=False, indent=2)}"}]
        
        # 대화 이력을 변환하여 추가 (Gemini 형식 → OpenAI 형식)
        for msg in messages:
            # Gemini의 'model' 역할을 'assistant'로 변경
            role = 'assistant' if msg['role'] == 'model' else msg['role']
            content = msg['parts'][0]['text']
            api_messages.append({"role": role, "content": content})
        
        response = client.chat.completions.create(
            model=model,
            messages=api_messages,  # Native History: 전체 메시지 리스트 전달
            temperature=temperature,
            response_format={"type": "json_object"}
        )
        
        # JSON 파싱
        content = response.choices[0].message.content
        result = json.loads(content)
        result['_model'] = 'gpt'
        result['_model_version'] = model  # 실제 모델명 기록
        
        # 스키마 검증
        return validate_ai_response(result)
        
    except json.JSONDecodeError as e:
        # JSON 파싱 실패 시 fallback
        return {
            'answer': content if 'content' in locals() else 'GPT 응답 파싱 실패',
            'claims': [],
            'evidence': [],
            'missing_info': ['JSON 응답 파싱 실패'],
            'confidence': 0.5,
            'actions_suggested': [],
            '_model': 'gpt',
            '_error': str(e)
        }
    except Exception as e:
        return {
            'answer': f'GPT 호출 실패: {str(e)}',
            'claims': [],
            'evidence': [],
            'missing_info': ['GPT API 호출 실패'],
            'confidence': 0.0,
            'actions_suggested': [],
            '_model': 'gpt',
            '_error': str(e)
        }


def _call_claude(messages, system_prompt, temperature=0.7):
    """Claude API 호출 (Native History 지원)"""
    if not settings.AI_MODELS['claude']['enabled']:
        raise Exception("Claude not initialized")
    
    client = settings.AI_MODELS['claude']['client']
    model = settings.AI_MODELS['claude']['model']
    
    try:
        # Claude는 JSON mode 직접 지원 안 함, system prompt에 JSON 요청 추가
        enhanced_prompt = f"{system_prompt}\n\n반드시 다음 JSON 형식으로만 응답하세요:\n{json.dumps(settings.AI_RESPONSE_SCHEMA, ensure_ascii=False, indent=2)}"
        
        # 대화 이력을 변환하여 추가 (Gemini 형식 → Anthropic 형식)
        api_messages = []
        for msg in messages:
            # Gemini의 'model' 역할을 'assistant'로 변경
            role = 'assistant' if msg['role'] == 'model' else msg['role']
            content = msg['parts'][0]['text']
            api_messages.append({"role": role, "content": content})
        
        response = client.messages.create(
            model=model,
            max_tokens=4096,
            temperature=temperature,
            system=enhanced_prompt,
            messages=api_messages  # Native History: 전체 메시지 리스트 전달
        )
        
        # JSON 파싱
        content = response.content[0].text
        result = json.loads(content)
        result['_model'] = 'claude'
        result['_model_version'] = model
        
        # 스키마 검증
        return validate_ai_response(result)
        
    except json.JSONDecodeError as e:
        # JSON 파싱 실패 시 fallback
        return {
            'answer': content if 'content' in locals() else 'Claude 응답 파싱 실패',
            'claims': [],
            'evidence': [],
            'missing_info': ['JSON 응답 파싱 실패'],
            'confidence': 0.5,
            'actions_suggested': [],
            '_model': 'claude',
            '_error': str(e)
        }
    except Exception as e:
        return {
            'answer': f'Claude 호출 실패: {str(e)}',
            'claims': [],
            'evidence': [],
            'confidence': 0.0,
            '_model': 'claude',
            '_error': str(e)
        }


def _call_all_models(full_message, system_prompt):
    """
    3두/2두 체계: 모든 활성화된 모델 호출 후 비교
    """
    results = {}
    
    for model_name, config in settings.AI_MODELS.items():
        if config['enabled']:
            try:
                if model_name == 'gemini':
                    results[model_name] = _call_gemini(full_message, system_prompt)
                elif model_name == 'gpt':
                    results[model_name] = _call_gpt(full_message, system_prompt)
                elif model_name == 'claude':
                    results[model_name] = _call_claude(full_message, system_prompt)
            except Exception as e:
                results[model_name] = {'error': str(e)}
    
    # 향후: 투표/합의 알고리즘 추가
    # 현재는 모든 결과 반환
    return {
        'answer': '멀티 모델 응답 (아래 참조)',
        'claims': [],
        'evidence': [],
        'missing_info': [],
        'confidence': 0.0,
        'actions_suggested': [],
        '_model': 'all',
        '_responses': results
    }
