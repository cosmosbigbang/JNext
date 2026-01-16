"""
Context Manager - 동적 맥락 관리 시스템
슬라이더 값에 따라 AI 맥락을 동적으로 조절
"""

from typing import Dict, List, Optional


class ContextManager:
    """동적 맥락 관리자"""
    
    @staticmethod
    def build_context(
        temperature: float,
        db_focus: int,
        project_id: Optional[str],
        user_message: str,
        conversation_history: List[Dict],
        project_db_context: str = "",
        project_prompt: str = ""
    ) -> Dict:
        """
        슬라이더 2개 값에 따라 맥락 구성
        
        Args:
            temperature: AI 창의성 (0.0-1.0)
            db_focus: DB 사용률 (0-100)
            project_id: 프로젝트 ID (None이면 일반 대화)
            user_message: 사용자 질문
            conversation_history: 대화 기록
            project_db_context: 프로젝트 DB 컨텍스트
            project_prompt: 프로젝트 시스템 프롬프트
            
        Returns:
            {
                'system_prompt': str,
                'full_message': str,
                'temperature': float,
                'weights': dict
            }
        """
        
        # 일반 대화 모드 (RAW 단계 - 아이디어 증폭)
        if not project_id:
            # 대화 모드도 슬라이더 적용 (DB 조절)
            weights = ContextManager._calculate_weights(db_focus)
            
            return {
                'system_prompt': """당신은 J님의 창의적 파트너 AI입니다. J님의 아이디어를 1차 증폭하여 RAW 데이터를 생성하는 역할입니다.

핵심 원칙:
- J님을 '사용자'가 아닌 'J님'이라고 호칭하세요
- 존댓말을 사용하고 창의적으로 대화하세요
- 대화 맥락을 철저히 유지하세요 (이전 대화에서 언급된 프로젝트/주제를 기억)
- 근거 없는 추측이나 거짓 정보는 절대 제공하지 마세요
- 확실하지 않은 내용은 "확실하지 않지만..." 또는 "추측하자면..."으로 명시하세요
- 구체적이고 실용적인 개선안을 제시하세요 (일반론 지양)""",
                'full_message': ContextManager._build_general_message(user_message, conversation_history),
                'temperature': temperature,  # 슬라이더에서 받은 값 사용
                'weights': weights  # DB 슬라이더로 조절
            }
        
        # 프로젝트 모드 - 가중치 계산
        weights = ContextManager._calculate_weights(db_focus)
        
        # 시스템 프롬프트 구성
        system_prompt = ContextManager._build_system_prompt(
            project_prompt, 
            weights,
            db_focus
        )
        
        # 전체 메시지 구성
        full_message = ContextManager._build_project_message(
            user_message,
            conversation_history,
            project_db_context,
            weights
        )
        
        return {
            'system_prompt': system_prompt,
            'full_message': full_message,
            'temperature': temperature,  # 슬라이더에서 받은 값 사용
            'weights': weights
        }
    
    @staticmethod
    def _calculate_weights(focus: int) -> Dict[str, int]:
        """
        슬라이더 값 → 가중치 변환
        
        DB OFF (focus=0): 대화 100%
        DB ON (focus=100): 대화 30% + DB 70%
        """
        
        if focus == 0:
            # DB OFF: 대화 이력만 100%
            return {
                'conversation': 100,
                'project': 0,
                'general': 0
            }
        
        # DB ON: 대화 30% 고정, 나머지는 DB vs 일반지식
        conversation_weight = 30
        project_weight = 70  # DB 전체
        general_weight = 0
        
        return {
            'conversation': conversation_weight,
            'project': project_weight,
            'general': general_weight
        }
    
    @staticmethod
    def _calculate_temperature(focus: int) -> float:
        """
        집중도 → temperature 변환
        
        높은 집중도 = 낮은 temperature (정확성)
        낮은 집중도 = 높은 temperature (창의성)
        """
        # focus 0-100 → temperature 0.7-0.2
        # 반비례 관계
        temp = 0.7 - (focus / 100 * 0.5)
        return round(temp, 2)
    
    @staticmethod
    def _build_system_prompt(project_prompt: str, weights: Dict, focus: int) -> str:
        """시스템 프롬프트 구성"""
        
        # 하이노밸런스 전용 System Prompt
        base_prompt = """너는 "하이노밸런스(HINOBALANCE)" 전담 AI다.

하이노밸런스는 일반 운동이 아니다.
이는 **불균형을 통해 신경계·관절·근막·중력 인식을 재조정하는
신체-뇌 통합 훈련 시스템**이다.

## ❗ 절대 규칙 (헌법)
1. 하이노밸런스는 "근비대, 반복, 고중량" 중심 설명을 하지 않는다.
2. 피로, 통증, 한계 돌파를 미덕으로 삼지 않는다.
3. 실패 개념을 사용하지 않는다.
4. 모든 동작은 "흔들림 → 무너짐 → 리셋" 구조로 설명한다.
5. 의학적 진단, 치료, 처방처럼 말하지 않는다.
6. 항상 **중립·차분·과장 없는 언어**를 사용한다.

## 🎯 핵심 철학
- 불균형은 오류가 아니라 **신호**
- 균형은 목표가 아니라 **과정 중 잠시 나타나는 상태**
- 움직임은 근육이 아니라 **신경계가 만든다**
- 정지는 힘이 아니라 **제어 능력**이다

## 🧠 설명 프레임
모든 설명은 다음 중 하나 이상을 반드시 포함한다:
- 신경계 재배열
- 고유수용성 감각
- 중력/가속도 인식
- 관절·근막 협응
- 자동보호시스템 완화
- 에너지 효율

## 🏃 동작 설명 규칙
- 횟수보다 **질감**을 먼저 설명
- 속도보다 **제동과 정지**
- 성공/실패 대신 **느낌 변화**
- 항상 마지막에:
  - "눈을 감고 3~5초 동작 재현" 옵션 제시

## 🧩 답변 스타일
- 짧고 명확
- 구조화된 문단
- 불필요한 강조 기호(** **) 사용 금지
- 과도한 비유 금지
- "~하면 됩니다" 대신 "~로 이어집니다" 표현 선호

## 🚫 금지 표현
- 근육이 커진다
- 지방을 태운다
- 폭발력 향상
- 한계 돌파
- 무조건 버텨라

너의 역할은
하이노밸런스를 **왜 하는지**, **몸에서 무엇이 바뀌는지**,
그리고 **언제 멈추고 리셋해야 하는지**를 설명하는 것이다.

## 💬 대화 맥락 유지 원칙
- "그거", "그것", "이전", "방금" 등은 바로 이전 대화를 참조한다
- J님이 주제를 명시하지 않으면 직전 대화의 주제를 이어간다
- 대화 이력에 나온 개념/용어를 절대 잊지 않는다
- 근거 없는 추측은 하지 않는다 (대화 이력이나 DB에 없으면 "확실하지 않습니다")

"""
        
        # 집중도에 따른 추가 지침
        if focus > 0:  # DB ON
            base_prompt += """
[DB 참고 지침]
- 프로젝트 DB 내용을 우선적으로 참고하세요
- DB에 없는 내용은 "DB에서 찾을 수 없습니다"라고 명시하세요
- 일반 지식과 혼동하지 마세요
"""
        else:  # DB OFF
            base_prompt += """
[대화 모드 지침]
- **대화 이력이 가장 중요**합니다 (100%)
- 직전 대화의 주제를 이어서 답변하세요
- J님이 "그거", "효과" 등만 언급하면 바로 이전 대화 주제를 참조하세요
"""
        
        return base_prompt
    
    @staticmethod
    def _build_general_message(user_message: str, conversation_history: List[Dict]) -> str:
        """일반 대화 메시지 구성"""
        
        message_parts = []
        
        # 최근 대화 (모바일 수준)
        if conversation_history:
            message_parts.append("=== 최근 대화 ===")
            for msg in conversation_history[-50:]:  # 50개 = 25턴 (모바일 수준)
                role = "J님" if msg['role'] == 'user' else "AI"
                message_parts.append(f"{role}: {msg['content']}")
            message_parts.append("\n=== 현재 질문 ===")
        
        message_parts.append(f"J님: {user_message}")
        
        return "\n".join(message_parts)
    
    @staticmethod
    def _build_project_message(
        user_message: str,
        conversation_history: List[Dict],
        project_db_context: str,
        weights: Dict
    ) -> str:
        """프로젝트 모드 메시지 구성"""
        
        message_parts = []
        
        # 1. 대화 맥락 (전체 이력 전달 - 모바일 수준)
        if conversation_history and weights['conversation'] > 0:
            message_parts.append(f"=== 대화 맥락 (가중치: {weights['conversation']}%) ===")
            # 가중치는 중요도를 의미, 개수는 전체 전달
            for msg in conversation_history[-50:]:  # 최대 50개 (25턴)
                role = "J님" if msg['role'] == 'user' else "AI"
                message_parts.append(f"{role}: {msg['content']}")
            message_parts.append("")
        
        # 2. 프로젝트 DB 맥락 (전체 전달)
        if project_db_context and weights['project'] > 0:
            message_parts.append(f"=== 프로젝트 DB (가중치: {weights['project']}%) ===")
            # 가중치는 중요도를 의미, DB는 전체 전달
            message_parts.append(project_db_context)
            message_parts.append("")
        
        # 3. 일반 지식 활용 안내
        if weights['general'] >= 30:
            message_parts.append(f"=== 일반 지식 활용 (가중치: {weights['general']}%) ===")
            message_parts.append("일반 상식과 지식도 자유롭게 활용하세요.")
            message_parts.append("")
        
        # 4. 현재 질문
        message_parts.append("=== 현재 질문 ===")
        message_parts.append(f"J님: {user_message}")
        
        return "\n".join(message_parts)
