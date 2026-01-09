"""
Firestore DB 서비스 레이어
모든 DB 조회/저장 로직을 통합 관리
"""
from firebase_admin import firestore
from datetime import datetime
from django.conf import settings


class FirestoreService:
    """Firestore 데이터베이스 통합 서비스"""
    
    @staticmethod
    def get_client():
        """Firestore 클라이언트 반환"""
        return firestore.client()
    
    @staticmethod
    def query_collections(collections=None, filters=None, limit=50):
        """
        여러 컬렉션에서 데이터 조회
        
        Args:
            collections: 조회할 컬렉션 리스트 (None이면 전체)
            filters: 필터 조건 dict (예: {'카테고리': '하이노워킹'})
            limit: 각 컬렉션당 최대 문서 수
            
        Returns:
            dict: {collection_name: [documents]}
        """
        db = FirestoreService.get_client()
        
        # 기본값: 3단계 컬렉션
        if collections is None:
            collections = [
                settings.COLLECTION_RAW,
                settings.COLLECTION_DRAFT,
                settings.COLLECTION_FINAL
            ]
        
        results = {}
        
        for collection_name in collections:
            try:
                query = db.collection(collection_name)
                
                # 필터 적용
                if filters:
                    for field, value in filters.items():
                        query = query.where(field, '==', value)
                
                # 문서 조회
                docs = query.limit(limit).stream()
                documents = []
                
                for doc in docs:
                    doc_data = doc.to_dict()
                    doc_data['_id'] = doc.id
                    doc_data['_collection'] = collection_name
                    
                    # DatetimeWithNanoseconds를 ISO 문자열로 변환
                    doc_data = FirestoreService._convert_timestamps(doc_data)
                    
                    documents.append(doc_data)
                
                results[collection_name] = documents
                
            except Exception as e:
                results[collection_name] = {'error': str(e)}
        
        return results
    
    @staticmethod
    def get_document(collection, doc_id):
        """
        특정 문서 조회
        
        Args:
            collection: 컬렉션명
            doc_id: 문서 ID
            
        Returns:
            dict: 문서 데이터 또는 None
        """
        db = FirestoreService.get_client()
        
        try:
            doc = db.collection(collection).document(doc_id).get()
            if doc.exists:
                doc_data = doc.to_dict()
                doc_data['_id'] = doc.id
                doc_data['_collection'] = collection
                return FirestoreService._convert_timestamps(doc_data)
            return None
        except Exception as e:
            raise Exception(f"문서 조회 실패: {str(e)}")
    
    @staticmethod
    def create_document(collection, data):
        """
        새 문서 생성
        
        Args:
            collection: 컬렉션명
            data: 저장할 데이터 dict
            
        Returns:
            str: 생성된 문서 ID
        """
        db = FirestoreService.get_client()
        
        try:
            # 타임스탬프 자동 추가
            data['생성일시'] = firestore.SERVER_TIMESTAMP
            data['수정일시'] = firestore.SERVER_TIMESTAMP
            
            # 문서 생성
            doc_ref = db.collection(collection).add(data)
            doc_id = doc_ref[1].id
            
            return doc_id
            
        except Exception as e:
            raise Exception(f"문서 생성 실패: {str(e)}")
    
    @staticmethod
    def update_document(collection, doc_id, data):
        """
        문서 업데이트
        
        Args:
            collection: 컬렉션명
            doc_id: 문서 ID
            data: 업데이트할 데이터 dict
            
        Returns:
            bool: 성공 여부
        """
        db = FirestoreService.get_client()
        
        try:
            doc_ref = db.collection(collection).document(doc_id)
            
            # 문서 존재 확인
            if not doc_ref.get().exists:
                raise Exception(f"문서를 찾을 수 없습니다: {collection}/{doc_id}")
            
            # 수정일시 업데이트
            data['수정일시'] = firestore.SERVER_TIMESTAMP
            
            # 문서 업데이트
            doc_ref.update(data)
            
            return True
            
        except Exception as e:
            raise Exception(f"문서 업데이트 실패: {str(e)}")
    
    @staticmethod
    def delete_document(collection, doc_id):
        """
        문서 삭제
        
        Args:
            collection: 컬렉션명
            doc_id: 문서 ID
            
        Returns:
            bool: 성공 여부
        """
        db = FirestoreService.get_client()
        
        try:
            doc_ref = db.collection(collection).document(doc_id)
            
            # 문서 존재 확인
            if not doc_ref.get().exists:
                raise Exception(f"문서를 찾을 수 없습니다: {collection}/{doc_id}")
            
            # 문서 삭제
            doc_ref.delete()
            
            return True
            
        except Exception as e:
            raise Exception(f"문서 삭제 실패: {str(e)}")
    
    @staticmethod
    def search_by_keyword(collections, keyword, fields=['제목', '내용'], limit=50):
        """
        키워드로 문서 검색 (간단한 구현)
        
        Args:
            collections: 검색할 컬렉션 리스트
            keyword: 검색 키워드
            fields: 검색할 필드 리스트
            limit: 최대 결과 수
            
        Returns:
            list: 매칭된 문서 리스트
        """
        results = []
        
        # 컬렉션 조회
        all_docs = FirestoreService.query_collections(collections, limit=limit)
        
        # 키워드 매칭 (클라이언트 측 필터링)
        for collection_name, documents in all_docs.items():
            if isinstance(documents, list):
                for doc in documents:
                    # 각 필드에서 키워드 검색
                    for field in fields:
                        if field in doc and keyword in str(doc[field]):
                            results.append(doc)
                            break
        
        return results
    
    @staticmethod
    def _convert_timestamps(doc_data):
        """DatetimeWithNanoseconds를 ISO 문자열로 변환"""
        for key, value in doc_data.items():
            if hasattr(value, 'isoformat'):
                doc_data[key] = value.isoformat()
        return doc_data
    
    @staticmethod
    def format_db_context(db_results):
        """
        DB 조회 결과를 AI 프롬프트용 텍스트로 포맷
        
        Args:
            db_results: query_collections() 결과
            
        Returns:
            str: 포맷된 텍스트
        """
        if not db_results:
            return "[DB 조회 결과: 데이터 없음]"
        
        context_parts = ["[Firestore DB 조회 결과]"]
        
        for collection_name, documents in db_results.items():
            if isinstance(documents, dict) and 'error' in documents:
                context_parts.append(f"\n{collection_name}: 조회 실패 - {documents['error']}")
                continue
            
            if not documents:
                context_parts.append(f"\n{collection_name}: 데이터 없음")
                continue
            
            context_parts.append(f"\n\n=== {collection_name} ({len(documents)}개 문서) ===")
            
            for doc in documents:
                doc_id = doc.get('_id', 'unknown')
                제목 = doc.get('제목', '제목 없음')
                카테고리 = doc.get('카테고리', '카테고리 없음')
                
                context_parts.append(f"\n[{doc_id}] {제목} ({카테고리})")
                
                # 주요 필드만 표시
                if '내용' in doc:
                    내용_미리보기 = str(doc['내용'])[:100] + "..." if len(str(doc['내용'])) > 100 else str(doc['내용'])
                    context_parts.append(f"  내용: {내용_미리보기}")
        
        return "\n".join(context_parts)
