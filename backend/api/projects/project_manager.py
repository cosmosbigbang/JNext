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
    
    def get_default_project(self) -> Optional[BaseProject]:
        """기본 프로젝트 반환 (하이노밸런스)"""
        return self._projects.get('hinobalance')


# 싱글톤 인스턴스 생성
project_manager = ProjectManager()
