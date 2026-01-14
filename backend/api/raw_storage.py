"""
Phase 3: AI 평가 및 RAW 저장 함수
"""
from firebase_admin import firestore
from datetime import datetime, timezone, timedelta
import json
from django.conf import settings

KST = timezone(timedelta(hours=9))


def evaluate_chat_value(user_message: str, ai_response: str) -> bool:
    """
    대화 가치 평가 (관대한 필터링)
    
    Args:
        user_message: 사용자 메시지
        ai_response: AI 응답
    
    Returns:
        bool: True (저장), False (스킵)
    """
    # 1단계: 명백한 잡담 키워드 체크
    trivial_keywords = [
        "안녕", "ㅎㅎㅎ", "ㅋㅋㅋ", "ㄱㅅ", "고마워", "감사",
        "좋아", "알겠어", "응", "ㅇㅇ", "넵", "오케이"
    ]
    
    message_lower = user_message.lower().strip()
    
    # 메시지가 5자 이하이고 잡담 키워드에 해당
    if len(message_lower) <= 5 and any(kw in message_lower for kw in trivial_keywords):
        print(f"[평가] 명백한 잡담: {user_message[:20]}")
        return False
    
    # 2단계: 애매한 경우 AI에게 물어보기 (매우 관대)
    try:
        if not settings.AI_MODELS['gemini-flash']['enabled']:
            # AI 없으면 무조건 저장 (안전)
            return True
        
        client = settings.AI_MODELS['gemini-flash']['client']
        model = settings.AI_MODELS['gemini-flash']['model']
        
        prompt = f"""다음 대화가 프로젝트 RAW 데이터로 저장할 가치가 있는지 평가하세요.

사용자: {user_message}
AI: {ai_response[:200]}...

**판단 기준:**
- 명백한 인사/감탄사/단순 반응만 no
- 질문, 아이디어, 의견, 피드백, 분석 요청 등은 모두 yes
- **애매하면 무조건 yes** (중요한 내용 놓치면 안 됨)

답변: yes 또는 no만 출력하세요."""

        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config={
                'temperature': 0.2,
                'max_output_tokens': 100,
            }
        )
        
        result = response.text.strip().lower()
        is_valuable = 'yes' in result
        
        print(f"[평가] AI 판단: {result} -> {'저장' if is_valuable else '스킵'}")
        return is_valuable
        
    except Exception as e:
        print(f"[평가] AI 평가 실패: {e}, 안전하게 저장")
        return True  # 에러 시 안전하게 저장


def analyze_and_save_raw(project_id: str, user_message: str, ai_response: str, chat_ref: str, model: str):
    """
    AI 분석 후 RAW 컬렉션에 저장
    
    Args:
        project_id: 프로젝트 ID (hinobalance, jbody 등)
        user_message: 사용자 원본 메시지
        ai_response: AI 응답 원본
        chat_ref: chat_history 문서 ID
        model: 사용된 AI 모델
    """
    try:
        if not settings.AI_MODELS['gemini-flash']['enabled']:
            print("[RAW 저장] AI 비활성화, 스킵")
            return
        
        client = settings.AI_MODELS['gemini-flash']['client']
        gemini_model = settings.AI_MODELS['gemini-flash']['model']
        
        # AI에게 분석 요청
        analysis_prompt = f"""다음 대화를 분석하여 JSON 형식으로 정리하세요.

사용자: {user_message}
AI: {ai_response}

반드시 다음 JSON 형식으로만 응답하세요:
{{
  "제목": "50자 이내 핵심 요약",
  "키워드": ["키워드1", "키워드2", "키워드3"],
  "카테고리": "주제 분류 (하이노워킹, 하이노골반, JBody 등)",
  "요약": "100자 이내 핵심 내용"
}}

**절대 규칙:**
1. AI 자기언급 완전 제거: "제가", "저는", "AI", "젠", "진", "클로", "어시스턴트" 등 모든 표현 삭제
2. 객관적 사실과 핵심 내용만 포함 (3인칭 시점)
3. 근거 없는 추측 금지
4. 확실하지 않으면 "불명확" 명시"""

        response = client.models.generate_content(
            model=gemini_model,
            contents=analysis_prompt,
            config={
                'temperature': 0.3,
                'max_output_tokens': 2048,
                'response_mime_type': 'application/json'
            }
        )
        
        metadata = json.loads(response.text)
        
        # AI 자기언급 제거 (후처리)
        import re
        ai_self_refs = r'(제가|저는|저희는|젠|젠시|진|클로|AI|어시스턴트|assistant|I am|I\'m|As an AI)'
        for key in ['제목', '요약']:
            if key in metadata and isinstance(metadata[key], str):
                metadata[key] = re.sub(ai_self_refs, '', metadata[key], flags=re.IGNORECASE)
                metadata[key] = re.sub(r'\s+', ' ', metadata[key]).strip()  # 공백 정리
        
        # Firestore 저장
        db = firestore.client()
        now = datetime.now(KST)
        timestamp = now.strftime('%Y%m%d_%H%M%S_%f')
        doc_id = f"{timestamp}"
        
        raw_data = {
            'id': doc_id,
            '제목': metadata.get('제목', '제목 없음'),
            '원본': user_message,
            'ai_응답': ai_response,
            '정리본': ai_response,  # 일단 원본과 동일, 나중에 정제 로직 추가
            '키워드': metadata.get('키워드', []),
            'category': metadata.get('카테고리', '기타'),
            '태그': [],
            '요약': metadata.get('요약', ''),
            'chat_ref': chat_ref,
            'project_id': project_id,
            'timestamp': now,
            '작성자': 'J님',
            '모델': model
        }
        
        # 상하위 구조: projects/{project_id}/raw/{doc_id}
        new_ref = db.collection('projects').document(project_id).collection('raw').document(doc_id)
        new_ref.set(raw_data)
        
        # chat_history 업데이트
        storage_path = f"projects/{project_id}/raw/{doc_id}"
        db.collection('chat_history').document(chat_ref).update({
            'raw_분석_완료': True,
            'raw_저장_위치': storage_path
        })
        
        print(f"[RAW 저장] 성공: {storage_path}")
        print(f"[RAW 저장] 제목: {metadata.get('제목')}")
        
    except Exception as e:
        print(f"[RAW 저장] 실패: {e}")
