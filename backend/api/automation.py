"""
하이노밸런스 자동화 메서드
자연어 명령 → Firestore CRUD 자동 실행
"""
from firebase_admin import firestore
from datetime import datetime
import google.generativeai as genai
import os

db = firestore.client()

class HinoAutomation:
    """하이노밸런스 자동화 클래스"""
    
    def __init__(self):
        self.db = db
        genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    # ===== 1. 문서 통합 =====
    def integrate_documents(self, category, output_name, versions=['summary', 'medium', 'full']):
        """
        카테고리의 모든 문서를 통합
        
        Args:
            category: '하이노이론', '하이노골반' 등
            output_name: '하이노전체이론', '하이노골반공통이론' 등
            versions: 생성할 버전 ['summary', 'medium', 'full']
        
        Returns:
            생성된 문서 ID 리스트
        """
        # 1. Firestore에서 해당 카테고리 문서 수집
        docs = self.db.collection('hino_raw').where('category', '==', category).stream()
        
        combined_content = ""
        doc_count = 0
        for doc in docs:
            data = doc.to_dict()
            combined_content += f"\n\n### {data.get('exercise_name')} ###\n\n"
            combined_content += data.get('content', '')
            doc_count += 1
        
        # 2. 버전별 생성
        created_ids = []
        for version in versions:
            if version == 'summary':
                content = self._create_summary(combined_content, 2000)
                doc_id = f"{output_name}_요약"
            elif version == 'medium':
                content = self._create_summary(combined_content, 10000)
                doc_id = f"{output_name}_중간"
            else:  # full
                content = combined_content
                doc_id = f"{output_name}_전체"
            
            # 3. hino_draft에 저장
            self.db.collection('hino_draft').document(doc_id).set({
                'exercise_name': doc_id,
                'title': f"{output_name} ({version})",
                'content': content,
                'category': category,
                'content_type': 'theory_integrated',
                'length_level': version,
                'source_count': doc_count,
                'created_at': datetime.now(),
                'status': 'draft'
            })
            created_ids.append(doc_id)
        
        return created_ids
    
    # ===== 2. 카테고리별 공통이론 생성 =====
    def create_category_theory(self, category):
        """
        카테고리의 공통 이론 생성
        
        Args:
            category: '하이노워밍', '하이노골반' 등
        """
        # 해당 카테고리 운동들 수집
        docs = self.db.collection('hino_raw').where('category', '==', category).stream()
        
        exercises = []
        for doc in docs:
            data = doc.to_dict()
            exercises.append({
                'name': data.get('exercise_name'),
                'content': data.get('content', '')
            })
        
        # AI에게 공통이론 생성 요청
        prompt = f"""
다음은 {category} 카테고리의 {len(exercises)}개 운동입니다.

이들의 공통 원리와 이론을 정리해주세요.

운동 목록:
{chr(10).join([f"- {ex['name']}" for ex in exercises])}

**구조:**
# {category} 공통 이론

## 1. 핵심 원리
## 2. 공통 효과
## 3. 주의사항
## 4. 난이도 체계
"""
        
        response = self.model.generate_content(prompt)
        
        # hino_draft에 저장
        doc_id = f"{category}_공통이론"
        self.db.collection('hino_draft').document(doc_id).set({
            'exercise_name': doc_id,
            'title': f"{category} 공통 이론",
            'content': response.text,
            'category': category,
            'content_type': 'category_theory',
            'exercise_count': len(exercises),
            'created_at': datetime.now(),
            'status': 'draft'
        })
        
        return doc_id
    
    # ===== 3. 개별 운동 상세 정리 =====
    def organize_exercise(self, exercise_name):
        """
        개별 운동 상세 정리
        
        Args:
            exercise_name: '하이노워밍벤치' 등
        """
        # hino_raw에서 원본 가져오기
        docs = self.db.collection('hino_raw').where('exercise_name', '==', exercise_name).stream()
        
        for doc in docs:
            data = doc.to_dict()
            raw_content = data.get('content', '')
            
            # AI에게 구조화 요청
            prompt = f"""
다음 운동을 체계적으로 정리해주세요.

운동명: {exercise_name}
원본 내용:
{raw_content}

**구조:**
# {exercise_name}

## 1. 동작 설명
(단계별로 명확하게)

## 2. 핵심 원리
(왜 이 동작이 효과적인가)

## 3. 효과
- 신체적 효과
- 신경학적 효과

## 4. 주의사항
(흔한 실수, 위험 요소)

## 5. 난이도 조절
(초급/중급/고급)
"""
            
            response = self.model.generate_content(prompt)
            
            # hino_draft에 저장
            self.db.collection('hino_draft').document(exercise_name).set({
                'exercise_name': exercise_name,
                'title': data.get('title'),
                'content': response.text,
                'category': data.get('category'),
                'content_type': 'exercise_detailed',
                'source': 'organized',
                'created_at': datetime.now(),
                'status': 'draft'
            })
            
            return exercise_name
        
        return None
    
    # ===== 4. 시트콤 시나리오 생성 =====
    def create_sitcom(self, exercise_name, scene_type='home'):
        """
        3인 시트콤 시나리오 생성
        
        Args:
            exercise_name: 운동명
            scene_type: 'home', 'office', 'street' 등
        """
        # 운동 정보 가져오기
        doc = self.db.collection('hino_draft').document(exercise_name).get()
        if not doc.exists:
            return None
        
        data = doc.to_dict()
        
        prompt = f"""
{exercise_name}을 소재로 3인 시트콤 시나리오를 만들어주세요.

**등장인물:**
- J (창시자): 하이노밸런스를 개발한 개발자, 열정적
- 지피 (AI 비서): 과학적 분석을 담당, 논리적
- 아내 (현실체크): 솔직한 반응, 공감 포인트

**장소:** {scene_type}
**분량:** 1분 정도 (대화 10~15줄)

운동 정보:
{data.get('content', '')[:500]}

**구조:**
[Scene: 장소 설명]

J: (대사)
지피: (대사)
아내: (대사)
...

[효과: 동작 효과 설명]
"""
        
        response = self.model.generate_content(prompt)
        
        # hino_draft에 시트콤 추가
        sitcom_id = f"{exercise_name}_시트콤"
        self.db.collection('hino_draft').document(sitcom_id).set({
            'exercise_name': exercise_name,
            'title': f"{exercise_name} 시트콤",
            'content': response.text,
            'category': data.get('category'),
            'content_type': 'sitcom_scenario',
            'characters': ['J', '지피', '아내'],
            'scene_type': scene_type,
            'created_at': datetime.now(),
            'status': 'draft'
        })
        
        return sitcom_id
    
    # ===== 5. 밈 생성 =====
    def create_meme(self, exercise_name):
        """밈 이미지 텍스트 생성"""
        # TODO: 구현
        pass
    
    # ===== 6. 숏 스크립트 생성 =====
    def create_short(self, exercise_name, duration=45):
        """
        숏폼 영상 스크립트 생성
        
        Args:
            exercise_name: 운동명
            duration: 영상 길이 (초)
        """
        # TODO: 구현
        pass
    
    # ===== Helper Methods =====
    def _create_summary(self, full_text, target_length):
        """AI로 요약 생성"""
        prompt = f"""
다음 텍스트를 {target_length}자 내외로 요약해주세요.
핵심 개념과 원리 중심으로 정리하되, 중요한 문구는 유지하세요.

{full_text[:20000]}
"""
        response = self.model.generate_content(prompt)
        return response.text
    
    # ===== 자연어 명령 파싱 =====
    def execute_command(self, command):
        """
        자연어 명령 실행
        
        Examples:
            "하이노골반 4개를 통합해줘"
            "하이노워밍 공통이론 만들어줘"
            "하이노워밍벤치 상세 정리해줘"
            "하이노골반상하 시트콤 만들어줘"
        """
        # AI로 명령 파싱
        parse_prompt = f"""
다음 명령을 JSON으로 파싱해주세요.

명령: "{command}"

가능한 action:
- integrate: 문서 통합
- category_theory: 카테고리 공통이론
- organize: 개별 운동 정리
- sitcom: 시트콤 생성
- meme: 밈 생성
- short: 숏 스크립트 생성

JSON 형식:
{{
    "action": "integrate|category_theory|organize|sitcom|meme|short",
    "target": "대상 (카테고리명 또는 운동명)",
    "options": {{}}
}}
"""
        
        response = self.model.generate_content(parse_prompt)
        # JSON 파싱 후 실행
        # TODO: 구현
        
        return response.text


# ===== Django View에서 사용할 함수 =====
def auto_process(command):
    """
    자연어 명령을 받아 자동 처리
    
    Usage in views.py:
        from .automation import auto_process
        result = auto_process("하이노골반 공통이론 만들어줘")
    """
    automation = HinoAutomation()
    return automation.execute_command(command)
