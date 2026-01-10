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
    J님의 메시지에서 의도(Intent) 감지
    Phase 6: 자동 CRUD
    
    Returns:
        dict: {
            'intent': 'SAVE' | 'READ' | 'UPDATE' | 'DELETE' | 'NONE',
            'confidence': 0.0~1.0,
            'params': {...}
        }
    """
    message_lower = user_message.lower()
    
    # SAVE 의도 (명령형만 인식, 계획/미래형 제외)
    save_keywords = ['저장해', '저장해줘', '기록해', '보관해']
    # 제외: '저장하자', '저장할게', '저장할까' 등 계획/제안형
    save_excludes = ['저장하자', '저장할게', '저장할까', '저장하면', '저장되면']
    
    if any(keyword in message_lower for keyword in save_keywords) and \
       not any(keyword in message_lower for keyword in save_excludes):
        params = {
            'collection': 'hino_final' if any(k in message_lower for k in ['최종', 'final', '완료']) else 'hino_draft',
            'target': 'last_response'
        }
        return {
            'intent': 'SAVE',
            'confidence': 0.9,
            'params': params
        }
    
    # READ 의도 (데이터 조회 - 명확한 키워드만)
    read_keywords = ['검색', '가져와', '보여줘', '조회', 'read', 'show', '찾아줘', '목록']
    # '알려줘', '설명' 등은 제외 (AI 대화용)
    exclude_keywords = ['알려', '설명', '분석', '어때', '뭐야', '무엇']
    
    if any(keyword in message_lower for keyword in read_keywords) and \
       not any(keyword in message_lower for keyword in exclude_keywords):
        params = {'collections': []}
        
        # 컬렉션 필터링
        if 'draft' in message_lower or '초안' in message_lower:
            params['collections'].append('hino_draft')
        if 'final' in message_lower or '최종' in message_lower:
            params['collections'].append('hino_final')
        if 'raw' in message_lower or '원본' in message_lower:
            params['collections'].append('hino_raw')
        
        # 카테고리 필터링
        categories = ['하이노이론', '하이노워킹', '하이노스케이팅', '하이노철봉', '하이노기본']
        for category in categories:
            if category in user_message:
                params['category'] = category
                break
        
        return {
            'intent': 'READ',
            'confidence': 0.85,
            'params': params
        }
    
    # DELETE 의도
    delete_keywords = ['삭제', 'delete', '지워', '삭제해', '제거']
    if any(keyword in message_lower for keyword in delete_keywords):
        return {
            'intent': 'DELETE',
            'confidence': 0.9,
            'params': {'requires_approval': True}
        }
    
    # UPDATE 의도
    update_keywords = ['수정', 'update', '고쳐', '바꿔', '변경']
    if any(keyword in message_lower for keyword in update_keywords):
        return {
            'intent': 'UPDATE',
            'confidence': 0.85,
            'params': {'requires_approval': True}
        }
    
    # ORGANIZE 의도 (명확한 문서 정리 명령만)
    # 조건: "정리해서 저장", "합쳐서", "통합해서" 등 구체적 정리 액션
    organize_patterns = [
        ('정리', ['저장', '합쳐', '통합', 'draft', 'raw', 'final']),  # "정리" + 저장/통합 관련 키워드
        ('합쳐', []),  # "합쳐"는 단독으로도 ORGANIZE
        ('통합해', []),  # "통합해"도 단독 OK
    ]
    
    organize_triggered = False
    for primary_kw, secondary_kws in organize_patterns:
        if primary_kw in message_lower:
            # secondary_kws가 비어있으면 primary만으로 충분
            if not secondary_kws:
                organize_triggered = True
                break
            # secondary_kws가 있으면 하나라도 포함되어야 함
            if any(sec_kw in message_lower for sec_kw in secondary_kws):
                organize_triggered = True
                break
    
    if organize_triggered:
        params = {
            'auto_save': False,  # 기본적으로 자동 저장 안함
            'collection': None
        }
        
        # 저장 명령 포함 시 auto_save 활성화
        if any(k in message_lower for k in ['저장', 'save']):
            params['auto_save'] = True
            # 저장 위치 감지
            if 'raw' in message_lower or '원본' in message_lower:
                params['collection'] = 'hino_raw'
            elif 'draft' in message_lower or '초안' in message_lower:
                params['collection'] = 'hino_draft'
            elif 'final' in message_lower or '최종' in message_lower:
                params['collection'] = 'hino_final'
            else:
                params['collection'] = 'hino_draft'  # 기본값
        
        return {
            'intent': 'ORGANIZE',
            'confidence': 0.9,
            'params': params
        }
    
    # GENERATE_FINAL 의도 (최종본 생성/정리)
    generate_keywords = ['최종본', '종합해', '만들어']
    if any(keyword in message_lower for keyword in generate_keywords):
        params = {
            'mode': 'final' if '최종' in message_lower else 'draft',
            'category': None,
            'exercise_name': None,
            'include_keywords': [],
            'exclude_keywords': []
        }
        
        # 카테고리 감지
        categories = ['하이노이론', '하이노워킹', '하이노스케이팅', '하이노철봉', '하이노기본', '하이노밸런스']
        for category in categories:
            if category in user_message:
                params['category'] = category
                break
        
        # 운동명 감지 (카테고리 하위)
        exercise_patterns = ['기본', '패스트', '슬로우', 'X', '주먹', '폭당폭당', '크로스']
        for pattern in exercise_patterns:
            if pattern in user_message and params['category']:
                params['exercise_name'] = params['category'] + pattern
        
        # 포함/제외 키워드 추출
        if '포함' in user_message or '넣어' in user_message:
            # "기본, 패스트 포함" 형태 감지
            import re
            include_match = re.search(r'([\w\s,]+)\s*(포함|넣)', user_message)
            if include_match:
                keywords = include_match.group(1).replace(',', ' ').split()
                params['include_keywords'] = keywords
        
        if '빼' in user_message or '제외' in user_message:
            import re
            exclude_match = re.search(r'([\w\s,]+)\s*(빼|제외)', user_message)
            if exclude_match:
                keywords = exclude_match.group(1).replace(',', ' ').split()
                params['exclude_keywords'] = keywords
        
        # '전체' 키워드
        if '전체' in message_lower:
            params['all'] = True
        
        return {
            'intent': 'GENERATE_FINAL',
            'confidence': 0.9,
            'params': params
        }
    
    # NONE (일반 질문)
    return {
        'intent': 'NONE',
        'confidence': 1.0,
        'params': {}
    }


def call_ai_model(model_name, user_message, system_prompt, db_context):
    """
    AI 모델 호출 (멀티 모델 지원)
    
    Args:
        model_name: 'gemini-flash' | 'gemini-pro' | 'gpt' | 'claude' | 'all'
        user_message: J님의 메시지
        system_prompt: 시스템 프롬프트
        db_context: Firestore DB 데이터
    
    Returns:
        dict: JSON 응답 (AI_RESPONSE_SCHEMA 형식)
    """
    full_message = f"{db_context}\n\nJ님 질문: {user_message}"
    
    # Gemini 계열 (Flash/Pro)
    if model_name in ['gemini-flash', 'gemini-pro']:
        return _call_gemini(full_message, system_prompt, model_key=model_name)
    
    # 기본값 fallback
    elif model_name == 'gemini' or not model_name:
        return _call_gemini(full_message, system_prompt, model_key=settings.DEFAULT_AI_MODEL)
    
    elif model_name == 'gpt':
        return _call_gpt(full_message, system_prompt)
    
    elif model_name == 'claude':
        return _call_claude(full_message, system_prompt)
    
    elif model_name == 'all':
        # 3두 체계: 모든 모델 호출 후 비교
        return _call_all_models(full_message, system_prompt)
    
    else:
        raise ValueError(f"Unknown model: {model_name}")


def _call_gemini(full_message, system_prompt, model_key='gemini-pro'):
    """Gemini API 호출 (JSON 응답 강제)
    
    Args:
        model_key: 'gemini-flash' | 'gemini-pro'
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
                'temperature': 0.7,
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


def _call_gpt(full_message, system_prompt):
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
            temperature=0.7,
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


def _call_claude(full_message, system_prompt):
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
            temperature=0.7,
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
