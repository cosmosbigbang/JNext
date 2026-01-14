"""
Base Project Class
모든 프로젝트의 베이스 클래스
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional


class BaseProject(ABC):
    """프로젝트 베이스 클래스"""
    
    # 프로젝트 메타데이터
    project_id: str = "base"
    display_name: str = "기본 프로젝트"
    description: str = ""
    
    # Firestore 컬렉션 구조
    collections = {
        'raw': 'raw',
        'draft': 'draft',
        'final': 'final'
    }
    
    # 컨텐츠 타입
    content_types: List[str] = []
    
    # 필드 매핑
    field_mapping: Dict[str, str] = {
        'category': '카테고리',
        'title': '제목',
        'content': '내용',
        'full_text': '전체글',
        'created_at': '작성일시',
        'status': '상태'
    }
    
    def get_collection_name(self, stage: str) -> str:
        """
        Firestore 컬렉션 이름 반환 (Hierarchical 구조)
        
        Args:
            stage: 'raw', 'draft', 'final'
            
        Returns:
            str: 서브컬렉션 이름 (예: "raw", "draft", "final")
        """
        # projects/{project_id}/{subcollection} 구조를 위해 subcollection 이름만 반환
        return self.collections.get(stage, stage)
    
    def get_field_name(self, english_key: str) -> str:
        """영문 키를 프로젝트별 필드명으로 변환"""
        return self.field_mapping.get(english_key, english_key)
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """
        프로젝트 시스템 프롬프트 반환
        
        Returns:
            str: AI에게 전달할 시스템 프롬프트
        """
        pass
    
    @abstractmethod
    def get_db_context(self, limit: int = 50) -> str:
        """
        프로젝트 DB 컨텍스트 반환
        
        Args:
            limit: 최대 문서 수
            
        Returns:
            str: DB에서 가져온 컨텍스트 문자열
        """
        pass
