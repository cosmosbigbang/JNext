"""
Firestore 컬렉션 목록 확인
"""
import firebase_admin
from firebase_admin import credentials, firestore
from pathlib import Path

# Firebase 초기화
if not firebase_admin._apps:
    base_dir = Path(__file__).resolve().parent
    cred_path = base_dir.parent / 'jnext-service-account.json'
    cred = credentials.Certificate(str(cred_path))
    firebase_admin.initialize_app(cred)

db = firestore.client()

print("=" * 80)
print("Firestore 컬렉션 목록")
print("=" * 80)

# 모든 컬렉션 조회
collections = db.collections()

for collection in collections:
    print(f"\n컬렉션: {collection.id}")
    
    # 각 컬렉션의 문서 수 확인
    docs = collection.stream()
    doc_count = sum(1 for _ in docs)
    print(f"  문서 수: {doc_count}개")
    
    # 첫 번째 문서 미리보기
    first_doc = collection.limit(1).stream()
    for doc in first_doc:
        print(f"  예시 문서 ID: {doc.id}")
        data = doc.to_dict()
        print(f"  필드: {list(data.keys())}")
        break

print(f"\n{'=' * 80}")
