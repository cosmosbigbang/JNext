"""
HinoBalance Project
하이노밸런스 프로젝트 설정
"""

import re
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
        """하이노밸런스 시스템 프롬프트 (모바일 디폴트: 없음)"""
        return ""
    
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
    
    def get_db_context(self, limit: int = 50, category: str = None, keyword: str = None) -> str:
        """
        하이노밸런스 DB 컨텍스트 가져오기
        우선순위: hino_final(최종) → hino_draft(초안) → hino_raw(원본)
        
        Args:
            limit: 최대 문서 수
            category: 특정 카테고리 필터 (옵션)
            keyword: 키워드 검색 (제목, 내용에서 검색, 띄어쓰기 무시, OR 검색)
            
        Returns:
            str: DB 컨텍스트 (모든 컬렉션 통합)
        """
        db = firestore.client()
        
        # 키워드 정규화 및 분리 (띄어쓰기 제거, 단어별 분리)
        normalized_keywords = []
        if keyword:
            # 띄어쓰기와 특수문자로 분리
            words = re.split(r'[\s,\.]+', keyword)
            for word in words:
                clean_word = word.replace(' ', '').lower().strip()
                if len(clean_word) > 1:  # 1글자 단어는 제외
                    normalized_keywords.append(clean_word)
        
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
                
                # 키워드 검색은 클라이언트 측에서 필터링 (Firestore는 LIKE 미지원)
                docs = query.limit(limit * 3).stream()  # 키워드 필터링 위해 더 많이 가져옴
                doc_count = 0
                
                for doc in docs:
                    data = doc.to_dict()
                    
                    # 문서 정보 추출 (다양한 필드명 지원 - 영문 우선)
                    category_text = data.get('category') or data.get('카테고리') or 'N/A'
                    title = data.get('제목') or data.get('title') or 'N/A'
                    
                    # 내용 필드 우선순위: 전체글 > 내용 > content > ai_응답
                    content = (data.get('전체글') or 
                              data.get('내용') or 
                              data.get('full_text') or 
                              data.get('content') or 
                              data.get('ai_응답') or
                              '')
                    
                    if not content:
                        continue
                    
                    # 키워드 검색 (OR 조건: 단어 중 하나라도 매칭되면 포함)
                    if normalized_keywords:
                        normalized_title = title.replace(' ', '').lower()
                        normalized_content = content.replace(' ', '').lower()
                        
                        # 키워드 중 하나라도 제목 또는 내용에 있으면 포함
                        matched = False
                        for kw in normalized_keywords:
                            if kw in normalized_title or kw in normalized_content:
                                matched = True
                                break
                        
                        if not matched:
                            continue
                    
                    doc_count += 1
                    
                    # 컨텍스트 구성 (최대 800자)
                    doc_context = f"""
[출처: {label}]
카테고리: {category_text}
제목: {title}
내용:
{content[:800]}
{'...(생략)' if len(content) > 800 else ''}
"""
                    context_parts.append(doc_context)
                    
                    # limit 도달 시 중단
                    if doc_count >= limit:
                        break
                
                if doc_count > 0:
                    print(f"[HinoBalance] Loaded {doc_count} docs from projects/{self.project_id}/{subcollection}")
                    
            except Exception as e:
                print(f"[HinoBalance] Error loading projects/{self.project_id}/{subcollection}: {e}")
                continue
        
        if not context_parts:
            if normalized_keywords:
                return f"[하이노밸런스 DB에서 '{keyword}' 관련 데이터를 찾을 수 없습니다]"
            return "[하이노밸런스 DB에 데이터가 없습니다]"
        
        return "\n\n".join(context_parts[:limit])
