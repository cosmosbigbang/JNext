"""
HinoBalance Project
하이노밸런스 프로젝트 설정
"""

from .base import BaseProject
from firebase_admin import firestore


class HinoBalanceProject(BaseProject):
    """하이노밸런스 프로젝트"""
    
    project_id = "hinobalance"  # hino → hinobalance 변경
    display_name = "하이노밸런스"
    description = "J님의 하이노밸런스 운동 이론 및 실전 관리"
    
    # 메인 카테고리
    main_categories = {
        '이론': ['요약', '중간', '전체', '가치'],
        '실전': ['하이노워밍', '하이노골반', '하이노워킹', '하이노스케이팅', '하이노풋삽', '하이노철봉'],
        '밈': [],
        '숏': []
    }
    
    # 실전 운동 카테고리
    exercise_categories = [
        '하이노워밍',
        '하이노골반',
        '하이노워킹',
        '하이노스케이팅',
        '하이노풋삽',
        '하이노철봉'
    ]
    
    def get_system_prompt(self) -> str:
        """하이노밸런스 시스템 프롬프트 (진·젠 축소 버전)"""
        return """당신은 J님과 함께 하이노밸런스를 개발한 AI입니다.

【정의】
가속도 제어와 편측성 불안정을 이용한 신경계 재배열 운동
- 핵심: 근력 아닌 움직임 제어, 신경계 재배열, 에너지 흐름
- 차별: 웨이트(근비대) vs 필라테스(정렬) vs 하이노(관성·신경)

【철학】
- 불균형=신호(오류 아님), 균형=과정(목표 아님)
- 한발=생명, 두발=정지=죽음
- 흔들림→정보, 무너짐→피드백, 리셋→업데이트

【J님 맥락】
9개월 GPT 개발 → GPT 다운 사고 → 허리 통증
타이핑으로 어깨/목 악화, 즉시 효과 중시

【톤】
중립·차분·과장 없음
"~하면 됩니다" ❌ → "~로 이어집니다" ✅
"J님" 호칭 (절대 "사용자" 금지)

【출력】
숫자 목록 1.2.3. (마크다운 **##-`> 금지)
점수 X/10 + 한 줄 정의
"견갑 고정 해제→경추 정체 제거" (추상 금지)

【개별성 우선】 ★ 가장 중요
이 운동만의 타겟·효과·타이밍 명시
일반론(불안정성, 가속도) 나열 금지

【금지】
근비대, 지방연소, 의학 진단/치료

【안전 지침】
- 정지 시간: 실력에 맞춰 2초→3초→5초 조절
- 무너지면 즉시 리셋 (버티지 않음)
- 하루 컨디션 따라 자동 강도 조절

【마지막 옵션】
모든 동작 설명 끝에 "눈 감고 3-5초 동작 재현" 제시
"""
    
    def get_menu_structure(self):
        """
        카테고리 기반 메뉴 구조 자동 생성
        카테고리 분류 = 앱 메뉴 (자동화 핵심)
        
        Returns:
            dict: 메뉴 구조 (앱에서 바로 사용 가능)
        """
        return {
            'project': self.project_id,
            'name': self.display_name,
            'categories': [
                {
                    'id': '이론',
                    'name': '이론',
                    'icon': '📚',
                    'subcategories': [
                        {'id': '요약', 'name': '요약'},
                        {'id': '중간', 'name': '중간'},
                        {'id': '전체', 'name': '전체'},
                        {'id': '가치', 'name': '가치'}
                    ]
                },
                {
                    'id': '실전',
                    'name': '실전',
                    'icon': '💪',
                    'subcategories': [
                        {'id': '하이노워밍', 'name': '하이노워밍'},
                        {'id': '하이노골반', 'name': '하이노골반'},
                        {'id': '하이노워킹', 'name': '하이노워킹'},
                        {'id': '하이노스케이팅', 'name': '하이노스케이팅'},
                        {'id': '하이노풋삽', 'name': '하이노풋삽'},
                        {'id': '하이노철봉', 'name': '하이노철봉'}
                    ]
                },
                {
                    'id': '밈',
                    'name': '밈',
                    'icon': '😂',
                    'subcategories': []
                },
                {
                    'id': '숏',
                    'name': '숏',
                    'icon': '🎬',
                    'subcategories': []
                }
            ]
        }
    
    def get_content_by_category(self, category: str, subcategory: str = None, limit: int = 20):
        """
        카테고리별 컨텐츠 조회 (앱 메뉴 선택 시 사용)
        
        Args:
            category: 메인 카테고리 (이론/실전/밈/숏)
            subcategory: 서브 카테고리 (요약, 하이노워밍 등)
            limit: 최대 문서 수
            
        Returns:
            list: 컨텐츠 리스트
        """
        db = firestore.client()
        contents = []
        
        # 우선순위: 최종 → 초안 → 원본 (상하위)
        collections = ['final', 'draft', 'raw']
        
        for subcollection in collections:
            try:
                # 상하위 구조
                query = db.collection('projects').document(self.project_id).collection(subcollection)
                
                # 카테고리 필터링
                if subcategory:
                    query = query.where('category', '==', subcategory)
                elif category:
                    # 메인 카테고리로 필터 (실전 → 하이노* 운동들)
                    if category == '실전':
                        for exercise in self.exercise_categories:
                            sub_query = db.collection('projects').document(self.project_id).collection(subcollection).where('카테고리', '==', exercise).limit(limit)
                            for doc in sub_query.stream():
                                data = doc.to_dict()
                                contents.append({
                                    'id': doc.id,
                                    'category': data.get('카테고리'),
                                    'title': data.get('제목') or data.get('title'),
                                    'content': data.get('전체글') or data.get('내용') or data.get('content'),
                                    'source': f"projects/{self.project_id}/{subcollection}"
                                })
                        continue
                    else:
                        query = query.where('category', 'in', self.main_categories.get(category, []))
                
                docs = query.limit(limit).stream()
                
                for doc in docs:
                    data = doc.to_dict()
                    contents.append({
                        'id': doc.id,
                        'category': data.get('category'),
                        'title': data.get('제목') or data.get('title'),
                        'content': data.get('전체글') or data.get('내용') or data.get('content'),
                        'source': f"projects/{self.project_id}/{subcollection}"
                    })
                
                if len(contents) >= limit:
                    break
                    
            except Exception as e:
                print(f"[HinoBalance] Error querying projects/{self.project_id}/{subcollection}: {e}")
                continue
        
        return contents[:limit]
    
    def get_db_context(self, limit: int = 50, category: str = None) -> str:
        """
        하이노밸런스 DB 컨텍스트 가져오기
        우선순위: hino_final(최종) → hino_draft(초안) → hino_raw(원본)
        
        Args:
            limit: 최대 문서 수
            category: 특정 카테고리 필터 (옵션)
            
        Returns:
            str: DB 컨텍스트 (모든 컬렉션 통합)
        """
        db = firestore.client()
        
        context_parts = []
        # 우선순위 순서: 최종 → 초안 → 원본 (상하위 구조)
        collections = [
            ('final', '최종본'),
            ('draft', '초안'),
            ('raw', '원본')
        ]
        
        for subcollection, label in collections:
            try:
                # 상하위 구조: projects/hinobalance/{subcollection}
                query = db.collection('projects').document(self.project_id).collection(subcollection)
                
                # 카테고리 필터 적용 (옵션)
                if category:
                    query = query.where('category', '==', category)
                
                # order_by는 모든 문서에 해당 필드가 있어야 하므로 제거
                # (기존 문서: 시간, 새 문서: timestamp - 혼재 시 에러)
                
                docs = query.limit(limit).stream()
                doc_count = 0
                
                for doc in docs:
                    data = doc.to_dict()
                    doc_count += 1
                    
                    # 문서 정보 추출 (다양한 필드명 지원 - 영문 우선)
                    category = data.get('category') or data.get('카테고리') or 'N/A'
                    title = data.get('제목') or data.get('title') or 'N/A'
                    
                    # 내용 필드 우선순위: 전체글 > 내용 > content
                    content = (data.get('전체글') or 
                              data.get('내용') or 
                              data.get('full_text') or 
                              data.get('content') or 
                              '')
                    
                    if not content:
                        continue
                    
                    # 컨텍스트 구성 (최대 800자)
                    doc_context = f"""
[출처: {label}]
카테고리: {category}
제목: {title}
내용:
{content[:800]}
{'...(생략)' if len(content) > 800 else ''}
"""
                    context_parts.append(doc_context)
                
                if doc_count > 0:
                    print(f"[HinoBalance] Loaded {doc_count} docs from projects/{self.project_id}/{subcollection}")
                    
            except Exception as e:
                print(f"[HinoBalance] Error loading projects/{self.project_id}/{subcollection}: {e}")
                continue
        
        if not context_parts:
            return "[하이노밸런스 DB에 데이터가 없습니다]"
        
        return "\n\n".join(context_parts[:limit])
