"""
AI 세션 학습 관리
진, 젠의 학습 내용을 세션 간 보존
"""
from firebase_admin import firestore
from datetime import datetime
from .ai_service import call_ai_model


def save_session_learning(project_id, model, learning_summary):
    """
    세션 학습 내용 저장
    
    Args:
        project_id: 프로젝트 ID (hinobalance 등)
        model: AI 모델명 (gemini-pro, gpt 등)
        learning_summary: 학습 요약 내용
    """
    db = firestore.client()
    
    model_alias = {
        'gemini-pro': '젠',
        'gpt': '진',
        'claude': '클로'
    }.get(model, model)
    
    db.collection('session_learning').add({
        'project_id': project_id,
        'model': model,
        'model_alias': model_alias,
        'summary': learning_summary,
        'timestamp': datetime.now()
    })
    
    print(f"[Session Learning] {model_alias}의 학습 내용 저장 완료")


def load_recent_learning(project_id, limit=5):
    """
    최근 세션 학습 내용 로드
    
    Args:
        project_id: 프로젝트 ID
        limit: 최대 개수
        
    Returns:
        str: 학습 내용 통합 텍스트
    """
    db = firestore.client()
    
    docs = db.collection('session_learning')\
        .where('project_id', '==', project_id)\
        .order_by('timestamp', direction=firestore.Query.DESCENDING)\
        .limit(limit)\
        .stream()
    
    learning_texts = []
    for doc in docs:
        data = doc.to_dict()
        model_alias = data.get('model_alias', '')
        summary = data.get('summary', '')
        timestamp = data.get('timestamp', '')
        
        learning_texts.append(f"[{model_alias} - {timestamp}]\n{summary}\n")
    
    if learning_texts:
        return "\n".join(reversed(learning_texts))  # 시간순 정렬
    else:
        return ""


def auto_summarize_learning(conversation_history, model, project_id):
    """
    대화 기록을 기반으로 학습 내용 자동 요약
    
    Args:
        conversation_history: 최근 대화 기록
        model: 현재 AI 모델
        project_id: 프로젝트 ID
        
    Returns:
        str: 요약된 학습 내용
    """
    # 최근 10개 대화만 요약
    recent_chats = conversation_history[-10:] if len(conversation_history) > 10 else conversation_history
    
    # 대화 텍스트 구성
    chat_text = "\n".join([
        f"{chat.get('role', 'user')}: {chat.get('content', '')[:200]}"  # 각 200자로 제한
        for chat in recent_chats
    ])
    
    # AI에게 요약 요청
    summary_prompt = f"""다음은 J님과의 최근 대화 내용입니다.
이 대화에서 다음 항목들을 간단히 요약해주세요:

1. J님이 선호하는 표현 방식이나 스타일
2. 반복적으로 나타난 피드백 패턴
3. 개선 요청 사항
4. 다음 세션에서 참고할 중요 포인트

대화 내용:
{chat_text}

**간단 요약 (200자 이내)**:"""
    
    try:
        response = call_ai_model(
            model_name=model,
            user_message=summary_prompt,
            system_prompt="J님과의 대화를 분석하여 학습 내용을 간단히 요약하는 AI입니다.",
            db_context="",
            mode='learning',
            conversation_history=[],
            temperature=0.3  # 사실 중심
        )
        
        summary = response.get('answer', '요약 실패')
        
        # 저장
        save_session_learning(project_id, model, summary)
        
        return summary
        
    except Exception as e:
        print(f"[Session Learning] 자동 요약 실패: {e}")
        return ""


def check_and_auto_summarize(conversation_history, model, project_id):
    """
    대화 개수 확인 후 자동 요약 실행
    
    Args:
        conversation_history: 전체 대화 기록
        model: 현재 AI 모델
        project_id: 프로젝트 ID
        
    Returns:
        bool: 요약 실행 여부
    """
    # 대화 개수 확인 (10개마다)
    total_chats = len(conversation_history)
    
    if total_chats > 0 and total_chats % 10 == 0:
        print(f"[Session Learning] 대화 {total_chats}개 도달. 자동 요약 시작...")
        auto_summarize_learning(conversation_history, model, project_id)
        return True
    
    return False
