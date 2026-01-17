"""
Phase 3: AI 평가 및 RAW 저장 함수
"""
from firebase_admin import firestore
from datetime import datetime, timezone, timedelta
import json
import re
import logging
from django.conf import settings

logger = logging.getLogger(__name__)
KST = timezone(timedelta(hours=9))


def evaluate_chat_value(user_message: str, ai_response: str) -> bool:
    """
    응답 저장 여부 판단 - 범용 필터링 (프로젝트 무관)
    
    철학:
    - AI 자유도 최대 보장
    - 프로젝트 확장성 확보
    - 명백히 쓸모없는 것만 제거
    
    Args:
        user_message: 사용자 메시지 (참고용)
        ai_response: AI 응답
    
    Returns:
        bool: True (저장), False (스킵)
    """
    
    # 1. 빈 응답
    if not ai_response or len(ai_response.strip()) < 10:
        print(f"[평가] 빈 응답 - 스킵")
        return False
    
    # 2. 명백한 API 에러 메시지
    if ai_response.startswith("Error:") or ai_response.startswith("API Error"):
        print(f"[평가] API 에러 - 스킵")
        return False
    
    # 3. 일상 인사만 (의미 없음)
    인사_패턴 = ["안녕하세요", "감사합니다", "네 알겠습니다", "좋은 하루", "또 뵙겠습니다"]
    if any(pattern in ai_response for pattern in 인사_패턴) and len(ai_response) < 50:
        print(f"[평가] 일상 인사만 - 스킵")
        return False
    
    # 4. 확인 응답만 ("네", "알겠습니다" 등)
    짧은_응답 = ["네", "네.", "알겠습니다", "알겠습니다.", "확인했습니다", "확인했습니다."]
    if ai_response.strip() in 짧은_응답:
        print(f"[평가] 확인 응답만 - 스킵")
        return False
    
    # 나머지는 모두 저장 → AI 자유도 보장 ✅
    print(f"[평가] 저장 대상 ({len(ai_response)}자)")
    return True


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
        
        metadata = json.loads(response.text)
        
        # AI 자기언급 제거 (후처리)
        ai_self_refs = r'(제가|저는|저희는|젠|젠시|진|클로|AI|어시스턴트|assistant|I am|I\'m|As an AI)'
        for key in ['제목', '요약']:
            if key in metadata and isinstance(metadata[key], str):
                metadata[key] = re.sub(ai_self_refs, '', metadata[key], flags=re.IGNORECASE)
                metadata[key] = re.sub(r'\s+', ' ', metadata[key]).strip()  # 공백 정리
        
        # 🔍 품질 검증: 일반론/엉터리 감지 (강화)
        quality_issues = []
        
        # 1. J님 원본 키워드 누락 체크
        user_keywords = set(re.findall(r'[\w가-힣]+', user_message.lower()))
        response_text = ai_response.lower()
        
        # J님이 말씀한 핵심 키워드 중 5개 이상 누락 시 경고
        missing_keywords = [kw for kw in user_keywords if len(kw) > 2 and kw not in response_text]
        if len(missing_keywords) > 5:
            quality_issues.append(f"J님 키워드 {len(missing_keywords)}개 누락")
        
        # 2. 일반론 키워드 감지 (강화)
        generic_phrases = [
            '일반적으로', '보통', '대체로', '흔히', '전형적으로',
            '접근성', '비용 효율', '경쟁력', '생존 가능성',
            '파트너십', '게임 요소', '사용자 경험',
            '여러 의미', '다양한 해석', '맥락에 따라',
            '전신 신경계 활성화', '균형 감각', '코어 안정성',  # 하이노 일반론
            '협응력 향상', '신체 인지 능력', '근육 활성화'  # 추상적 표현
        ]
        generic_count = sum(1 for phrase in generic_phrases if phrase in ai_response)
        if generic_count >= 3:
            quality_issues.append(f"일반론 키워드 {generic_count}개 감지")
        
        # 3. 구조화된 답변 확인 (필수 필드 체크)
        required_keywords = ['타겟', '효과', '타이밍']
        missing_structure = [kw for kw in required_keywords if kw not in ai_response]
        if missing_structure:
            quality_issues.append(f"필수 구조 누락: {', '.join(missing_structure)}")
        
        # 4. 너무 짧은 답변
        if len(ai_response) < 300:
            quality_issues.append("답변 너무 짧음 (300자 미만)")
        
        # 5. 구체성 체크 (화살표 표현 있는지)
        if '→' not in ai_response and '->' not in ai_response:
            quality_issues.append("구체적 메커니즘 설명 부족 (화살표 없음)")
        
        # 품질 점수 계산 (0~100)
        quality_score = 100
        quality_score -= len(missing_keywords) * 2  # 누락 키워드당 -2점
        quality_score -= generic_count * 10  # 일반론당 -10점
        quality_score -= len(missing_structure) * 15  # 구조 누락당 -15점
        if len(ai_response) < 300:
            quality_score -= 30
        if '→' not in ai_response and '->' not in ai_response:
            quality_score -= 20
        if len(ai_response) < 200:
            quality_score -= 30
        
        quality_score = max(0, quality_score)
        
        # 품질 점수 로깅 (저장은 진행, J님이 점수 확인 후 기준 조정)
        if quality_score < 60:
            logger.warning(f"[품질 낮음] {quality_score}점 (기준 60점)")
            logger.warning(f"[품질 문제] {', '.join(quality_issues)}")
        
        # Firestore 저장
        db = firestore.client()
        # UTC → KST 변환 (명확하게)
        now_utc = datetime.now(timezone.utc)
        now = now_utc.astimezone(KST)
        timestamp_str = now.strftime('%Y%m%d_%H%M%S_%f')
        doc_id = f"{timestamp_str}"
        
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
            'timestamp': now,  # Firestore Timestamp (UTC 자동 변환)
            'timestamp_kst': timestamp_str,  # KST 문자열 (한국 시간 표시용)
            '작성자': 'J님',
            '모델': model,
            # 품질 메타데이터
            '품질점수': quality_score,
            '품질이슈': quality_issues,
            '검증필요': quality_score < 60  # 60점 미만이면 J님 검토 필요
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
