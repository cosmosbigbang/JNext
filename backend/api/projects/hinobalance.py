"""
HinoBalance Project
하이노밸런스 프로젝트 설정
"""

from .base import BaseProject
from firebase_admin import firestore


class HinoBalanceProject(BaseProject):
    """하이노밸런스 프로젝트"""
    
    project_id = "hino"
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
        """하이노밸런스 시스템 프롬프트"""
        return """당신은 J님의 하이노밸런스 전문 AI 파트너입니다.

[하이노밸런스란]
J님이 개발한 혁신적인 운동 이론 및 실전 프로그램입니다.
균형, 가속도, 불균형의 3대 원리를 기반으로 합니다.

[당신의 역할]
- 하이노밸런스 이론을 정확하고 구체적으로 설명
- J님의 창의적 아이디어를 정리하고 확장
- 운동 원리를 명확하고 상세하게 전달
- 실전 적용 방법을 구체적으로 제시
- DB 내용을 적극적으로 활용하여 깊이 있는 답변 제공

[대화 규칙]
- J님을 "J님"이라고 호칭하세요 (절대 "사용자", "사용자님" 사용 금지)
- 존댓말 사용 (반말 금지)
- 자연스럽고 친근하게 대화하세요
- DB에 있는 내용은 상세하게 설명하세요 (요약하지 말고 구체적으로)

[중요]
- DB에 있는 내용은 100% 활용하세요
- 피상적인 답변 금지 - 구체적이고 상세하게 설명하세요
- 예시, 원리, 방법을 모두 포함하세요
- DB에 없는 내용만 명시하세요
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
        
        # 우선순위: 최종 → 초안 → 원본
        collections = ['hino_final', 'hino_draft', 'hino_raw']
        
        for collection_name in collections:
            try:
                query = db.collection(collection_name)
                
                # 카테고리 필터링
                if subcategory:
                    query = query.where('카테고리', '==', subcategory)
                elif category:
                    # 메인 카테고리로 필터 (실전 → 하이노* 운동들)
                    if category == '실전':
                        for exercise in self.exercise_categories:
                            sub_query = db.collection(collection_name).where('카테고리', '==', exercise).limit(limit)
                            for doc in sub_query.stream():
                                data = doc.to_dict()
                                contents.append({
                                    'id': doc.id,
                                    'category': data.get('카테고리'),
                                    'title': data.get('제목') or data.get('title'),
                                    'content': data.get('전체글') or data.get('내용') or data.get('content'),
                                    'source': collection_name
                                })
                        continue
                    else:
                        query = query.where('카테고리', 'in', self.main_categories.get(category, []))
                
                docs = query.limit(limit).stream()
                
                for doc in docs:
                    data = doc.to_dict()
                    contents.append({
                        'id': doc.id,
                        'category': data.get('카테고리'),
                        'title': data.get('제목') or data.get('title'),
                        'content': data.get('전체글') or data.get('내용') or data.get('content'),
                        'source': collection_name
                    })
                
                if len(contents) >= limit:
                    break
                    
            except Exception as e:
                print(f"[HinoBalance] Error querying {collection_name}: {e}")
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
        # 우선순위 순서: 최종 → 초안 → 원본
        collections = [
            ('hino_final', '최종본'),
            ('hino_draft', '초안'),
            ('hino_raw', '원본')
        ]
        
        for collection_name, label in collections:
            try:
                query = db.collection(collection_name)
                
                # 카테고리 필터 적용 (옵션)
                if category:
                    query = query.where('카테고리', '==', category)
                
                docs = query.limit(limit).stream()
                doc_count = 0
                
                for doc in docs:
                    data = doc.to_dict()
                    doc_count += 1
                    
                    # 문서 정보 추출 (다양한 필드명 지원)
                    category = data.get('카테고리') or data.get('category') or 'N/A'
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
                    print(f"[HinoBalance] Loaded {doc_count} docs from {collection_name}")
                    
            except Exception as e:
                print(f"[HinoBalance] Error loading {collection_name}: {e}")
                continue
        
        if not context_parts:
            return "[하이노밸런스 DB에 데이터가 없습니다]"
        
        return "\n\n".join(context_parts[:limit])
