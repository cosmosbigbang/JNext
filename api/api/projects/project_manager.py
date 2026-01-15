"""
Project Manager
프로젝트 관리 싱글톤
"""

from typing import Dict, Optional
from .base import BaseProject
from .hinobalance import HinoBalanceProject


class ProjectManager:
    """프로젝트 관리자 (싱글톤)"""
    
    _instance = None
    _projects: Dict[str, BaseProject] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize_projects()
        return cls._instance
    
    def _initialize_projects(self):
        """등록된 프로젝트 초기화 + Firestore에서 동적 프로젝트 로드"""
        # 1. 기본 프로젝트 등록
        self.register_project(HinoBalanceProject())
        
        # 2. Firestore에서 저장된 프로젝트 로드
        try:
            from firebase_admin import firestore
            db = firestore.client()
            
            projects_ref = db.collection('projects').stream()
            loaded_count = 0
            
            for doc in projects_ref:
                data = doc.to_dict()
                project_id = data.get('project_id')
                display_name = data.get('display_name')
                description = data.get('description', '')
                
                # 이미 등록된 프로젝트는 스킵
                if project_id and project_id not in self._projects:
                    self.create_project(project_id, display_name, description)
                    loaded_count += 1
            
            if loaded_count > 0:
                print(f"[ProjectManager] Loaded {loaded_count} projects from Firestore")
        except Exception as e:
            print(f"[ProjectManager] Failed to load projects from Firestore: {e}")
        
        print(f"[ProjectManager] Total {len(self._projects)} projects initialized")
    
    def register_project(self, project: BaseProject):
        """프로젝트 등록"""
        self._projects[project.project_id] = project
        print(f"[ProjectManager] Registered: {project.display_name}")
    
    def get_project(self, project_id: str) -> Optional[BaseProject]:
        """프로젝트 가져오기"""
        return self._projects.get(project_id)
    
    def list_projects(self) -> Dict[str, str]:
        """
        프로젝트 목록 반환
        
        Returns:
            {project_id: display_name}
        """
        return {
            pid: proj.display_name 
            for pid, proj in self._projects.items()
        }
    
    def create_project(self, project_id: str, display_name: str, description: str = "") -> BaseProject:
        """
        새 프로젝트 동적 생성
        
        Args:
            project_id: 프로젝트 ID (영문, 소문자, 언더스코어)
            display_name: 표시 이름
            description: 프로젝트 설명
            
        Returns:
            생성된 프로젝트 객체
        """
        # 이미 존재하는 프로젝트 확인
        if project_id in self._projects:
            return self._projects[project_id]
        
        # BaseProject를 상속한 동적 클래스 생성
        class DynamicProject(BaseProject):
            def get_system_prompt(self) -> str:
                """동적 생성 프로젝트의 기본 시스템 프롬프트 (간소화)"""
                return f"""당신은 '{self.display_name}' 프로젝트 전문 AI입니다.

[핵심만]
- J님 원본 기준으로 분석
- DB 자료 깊게 활용
- 구체적으로 (예시·원리·방법)

[대화]
- "J님" 호칭 ("사용자" 금지)
- 존댓말, 자연스럽게

[금지]
- 일반론, 마크다운 **굵게**, 이전 답변 복사
"""
            
            def get_db_context(self, limit: int = 50) -> str:
                """Firestore에서 프로젝트 DB 컨텍스트 가져오기 + docs 폴더 자동 검색"""
                try:
                    from firebase_admin import firestore
                    db = firestore.client()
                    
                    # RAW → DRAFT → FINAL 우선순위 (J님 원본이 가장 중요!)
                    context_parts = []
                    
                    for collection in ['raw', 'draft', 'final']:
                        try:
                            docs = db.collection('projects').document(self.project_id).collection(collection).limit(limit).stream()
                            for doc in docs:
                                data = doc.to_dict()
                                title = data.get('제목', data.get('title', 'N/A'))
                                # RAW는 전체 내용 표시 (요약 금지!)
                                if collection == 'raw':
                                    원본 = data.get('원본', '')
                                    ai_응답 = data.get('ai_응답', '')
                                    content = data.get('내용', data.get('content', data.get('전체글', '')))
                                    
                                    raw_full = f"""
📌 J님 원본 입력:
{원본}

AI 이전 응답:
{ai_응답[:300]}...

정리된 내용:
{content}
"""
                                    context_parts.append(f"[RAW - J님 원본] {title}\n{raw_full}")
                                else:
                                    content = data.get('내용', data.get('content', data.get('전체글', '')))
                                    context_parts.append(f"[{collection.upper()}] {title}: {content[:300]}")
                        except:
                            pass
                    
                    # DB에 데이터 없으면 docs 폴더 검색
                    if not context_parts:
                        import os
                        import re
                        
                        # 프로젝트 루트 찾기
                        current_dir = os.path.dirname(os.path.abspath(__file__))
                        project_root = os.path.abspath(os.path.join(current_dir, '..', '..', '..'))
                        docs_dir = os.path.join(project_root, 'docs')
                        
                        if os.path.exists(docs_dir):
                            # project_id, display_name으로 검색
                            search_keywords = [
                                self.project_id.lower(),
                                self.display_name.lower(),
                                self.project_id.replace('_', '').lower()
                            ]
                            
                            for filename in os.listdir(docs_dir):
                                if filename.endswith('.md'):
                                    filepath = os.path.join(docs_dir, filename)
                                    try:
                                        with open(filepath, 'r', encoding='utf-8') as f:
                                            content = f.read()
                                            
                                            # 키워드 검색 (대소문자 무시)
                                            if any(kw in content.lower() for kw in search_keywords):
                                                # 관련 섹션 추출 (최대 1000자)
                                                lines = content.split('\n')
                                                relevant_lines = []
                                                
                                                for i, line in enumerate(lines):
                                                    if any(kw in line.lower() for kw in search_keywords):
                                                        # 앞뒤 5줄씩 포함
                                                        start = max(0, i - 5)
                                                        end = min(len(lines), i + 15)
                                                        relevant_lines.extend(lines[start:end])
                                                
                                                if relevant_lines:
                                                    snippet = '\n'.join(relevant_lines)[:1000]
                                                    context_parts.append(f"[DOCS/{filename}]\n{snippet}")
                                    except:
                                        pass
                    
                    return '\n\n'.join(context_parts) if context_parts else "프로젝트 데이터가 아직 없습니다."
                except Exception as e:
                    return f"DB 조회 실패: {str(e)}"
        
        # 프로젝트 속성 설정
        new_project = DynamicProject()
        new_project.project_id = project_id
        new_project.display_name = display_name
        new_project.description = description or f"{display_name} 프로젝트"
        
        # Firestore에 프로젝트 메타데이터 저장
        try:
            from firebase_admin import firestore
            from datetime import datetime, timezone, timedelta
            db = firestore.client()
            KST = timezone(timedelta(hours=9))
            
            project_meta = {
                'project_id': project_id,
                'display_name': display_name,
                'description': new_project.description,
                'created_at': datetime.now(KST),
                'collections': ['raw', 'draft', 'final'],
                'creator': 'J님'
            }
            
            db.collection('projects').document(project_id).set(project_meta)
            print(f"[ProjectManager] Firestore 저장 완료: projects/{project_id}")
        except Exception as e:
            print(f"[ProjectManager] Firestore 저장 실패: {e}")
        
        # 메모리에 등록
        self.register_project(new_project)
        
        return new_project
    
    def get_default_project(self) -> Optional[BaseProject]:
        """기본 프로젝트 반환 (하이노밸런스)"""
        return self._projects.get('hinobalance')


# 싱글톤 인스턴스 생성
project_manager = ProjectManager()
