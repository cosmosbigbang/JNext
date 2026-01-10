"""
AI 서비스 추상화 레이어
멀티 모델 지원 (Gemini, GPT, Claude)
Phase 6: 의도 분류 (Intent Classification)
Phase 7: JSON 스키마 검증
"""
from django.conf import settings
import json


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
    """
    message = user_message.strip()
    message_lower = message.lower()
    
    # DB 목적어 체크 (CRUD 활성화)
    has_db = any(db in message_lower for db in ['db', 'database', '데이터베이스', '디비'])
    
    # SAVE (엄격: "저장해"만, "db" 불필요)
    if any(cmd in message_lower for cmd in ['저장해', '저장해줘', '기록해', '보관해']):
        # 제외: "저장해서", "저장하고" 등
        if not any(exc in message_lower for exc in ['저장해서', '저장해도', '저장하고', '저장하면']):
            params = {
                'collection': 'hino_final' if any(k in message_lower for k in ['최종', 'final', '완료']) else 'hino_draft',
                'target': 'last_response'
            }
            return {
                'intent': 'SAVE',
                'confidence': 0.95,
                'params': params
            }
    
    # DELETE (엄격: "db" 필수)
    if has_db and any(cmd in message_lower for cmd in ['삭제해', '삭제해줘', '지워', '지워줘', '제거해']):
        if not any(exc in message_lower for exc in ['삭제해서', '삭제하고', '삭제하면']):
            return {
                'intent': 'DELETE',
                'confidence': 0.95,
                'params': {'requires_approval': True}
            }
    
    # UPDATE (엄격: "db" 필수)
    if has_db and any(cmd in message_lower for cmd in ['수정해', '수정해줘', '고쳐', '고쳐줘', '바꿔', '바꿔줘', '변경해']):
        # 제외: "수정해서 보여달라" = ORGANIZE
        if not any(exc in message_lower for exc in ['수정해서', '수정해도', '수정하고', '수정하면']):
            return {
                'intent': 'UPDATE',
                'confidence': 0.95,
                'params': {'requires_approval': True}
            }
    
    # READ (엄격: "db" 또는 카테고리 필수)
    db_targets = ['하이노이론', '하이노워킹', '하이노스케이팅', '하이노철봉', '하이노기본', '하이노밸런스',
                  'draft', '초안', 'final', '최종', 'raw', '원본']
    
    has_category = any(cat in message_lower for cat in db_targets)
    
    if (has_db or has_category) and any(cmd in message_lower for cmd in ['검색해', '검색해줘', '찾아줘', '가져와', '가져와줘', '조회해', '보여줘', '보여주']):
        params = {'collections': []}
        
        # 컬렉션 필터링
        if 'draft' in message_lower or '초안' in message_lower:
            params['collections'].append('hino_draft')
        if 'final' in message_lower or '최종' in message_lower:
            params['collections'].append('hino_final')
        if 'raw' in message_lower or '원본' in message_lower:
            params['collections'].append('hino_raw')
        
        # 카테고리 필터링
        categories = ['하이노이론', '하이노워킹', '하이노스케이팅', '하이노철봉', '하이노기본', '하이노밸런스']
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


def call_ai_model(model_name, user_message, system_prompt, db_context, temperature=None, mode='hybrid'):
    """
    AI 모델 호출 (멀티 모델 지원)
    
    Args:
        model_name: 'gemini-flash' | 'gemini-pro' | 'gpt' | 'claude' | 'all'
        user_message: J님의 메시지
        system_prompt: 시스템 프롬프트
        db_context: Firestore DB 데이터
        temperature: 창의성 수준 (None이면 mode에 따라 자동 설정)
        mode: 'organize' | 'hybrid' | 'analysis'
    
    Returns:
        dict: JSON 응답 (AI_RESPONSE_SCHEMA 형식)
    """
    # Temperature 자동 설정 (mode에 따라)
    if temperature is None:
        temperature_map = {
            'organize': 0.3,  # 사실 중심, 환각 최소화
            'hybrid': 0.5,    # 균형
            'analysis': 0.7   # 창의성 허용
        }
        temperature = temperature_map.get(mode, 0.5)
    
    # 모델 정보 주입
    model_info_map = {
        'gemini-flash': '젠 (Gemini 2.5 Flash) - 빠르고 정확한 한글 AI',
        'gemini-pro': '젠시 (Gemini Pro) - 심층 분석 AI',
        'gpt': '진 (GPT-4o) - 창의적 추론 AI'
    }
    model_info = model_info_map.get(model_name, model_name)
    enhanced_prompt = f"[당신의 정체성]\n당신은 '{model_info}' 입니다.\n\n{system_prompt}"
    
    full_message = f"{db_context}\n\nJ님 질문: {user_message}"
    
    # Gemini 계열 (Flash/Pro)
    if model_name in ['gemini-flash', 'gemini-pro']:
        return _call_gemini(full_message, enhanced_prompt, model_key=model_name, temperature=temperature)
    
    # 기본값 fallback
    elif model_name == 'gemini' or not model_name:
        return _call_gemini(full_message, enhanced_prompt, model_key=settings.DEFAULT_AI_MODEL, temperature=temperature)
    
    elif model_name == 'gpt':
        return _call_gpt(full_message, enhanced_prompt, temperature=temperature)
    
    elif model_name == 'claude':
        return _call_claude(full_message, enhanced_prompt, temperature=temperature)
    
    elif model_name == 'all':
        # 3두 체계: 모든 모델 호출 후 비교
        return _call_all_models(full_message, system_prompt, temperature=temperature)
    
    else:
        raise ValueError(f"Unknown model: {model_name}")


def _call_gemini(full_message, system_prompt, model_key='gemini-pro', temperature=0.5):
    """Gemini API 호출 (JSON 응답 강제)
    
    Args:
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
        response = client.models.generate_content(
            model=model,
            contents=full_message,
            config={
                'system_instruction': system_prompt,
                'temperature': temperature,  # 모드별 temperature 적용
                'response_mime_type': 'application/json',  # JSON 강제
                'response_schema': settings.AI_RESPONSE_SCHEMA,  # 스키마 강제
            }
        )
        
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


def _call_gpt(full_message, system_prompt, temperature=0.7):
    """GPT-4o API 호출 (OpenAI)"""
    if not settings.AI_MODELS['gpt']['enabled']:
        raise Exception("GPT not initialized")
    
    client = settings.GPT_CLIENT
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": f"{system_prompt}\n\n반드시 다음 JSON 형식으로만 응답하세요:\n{json.dumps(settings.AI_RESPONSE_SCHEMA, ensure_ascii=False, indent=2)}"},
                {"role": "user", "content": full_message}
            ],
            temperature=temperature,
            response_format={"type": "json_object"}
        )
        
        # JSON 파싱
        content = response.choices[0].message.content
        result = json.loads(content)
        result['_model'] = 'gpt'
        result['_model_version'] = 'gpt-4o'
        
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


def _call_claude(full_message, system_prompt, temperature=0.7):
    """Claude API 호출"""
    if not settings.AI_MODELS['claude']['enabled']:
        raise Exception("Claude not initialized")
    
    client = settings.AI_MODELS['claude']['client']
    model = settings.AI_MODELS['claude']['model']
    
    try:
        # Claude는 JSON mode 직접 지원 안 함, system prompt에 JSON 요청 추가
        enhanced_prompt = f"{system_prompt}\n\n반드시 다음 JSON 형식으로만 응답하세요:\n{json.dumps(settings.AI_RESPONSE_SCHEMA, ensure_ascii=False, indent=2)}"
        
        response = client.messages.create(
            model=model,
            max_tokens=4096,
            temperature=temperature,
            system=enhanced_prompt,
            messages=[
                {"role": "user", "content": full_message}
            ]
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
