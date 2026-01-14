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
        """등록된 프로젝트 초기화"""
        self.register_project(HinoBalanceProject())
        print("[ProjectManager] Projects initialized")
    
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
            pass
        
        # 프로젝트 속성 설정
        new_project = DynamicProject()
        new_project.project_id = project_id
        new_project.display_name = display_name
        new_project.description = description or f"{display_name} 프로젝트"
        
        # 등록
        self.register_project(new_project)
        
        return new_project
    
    def get_default_project(self) -> Optional[BaseProject]:
        """기본 프로젝트 반환 (하이노밸런스)"""
        return self._projects.get('hinobalance')


# 싱글톤 인스턴스 생성
project_manager = ProjectManager()
