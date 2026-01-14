"""
구 Firestore 컬렉션 삭제 (hino_raw, hino_draft)
Hierarchical 구조(projects/hinobalance/raw, draft, final)만 유지
"""

import firebase_admin
from firebase_admin import credentials, firestore
from pathlib import Path

# Firebase 초기화
project_root = Path(__file__).parent.parent
cred_path = project_root / "jnext-service-account.json"
cred = credentials.Certificate(str(cred_path))

if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

db = firestore.client()

def delete_collection(collection_name, batch_size=100):
    """컬렉션 전체 삭제"""
    coll_ref = db.collection(collection_name)
    docs = coll_ref.limit(batch_size).stream()
    deleted = 0

    for doc in docs:
        print(f'  삭제 중: {doc.id}')
        doc.reference.delete()
        deleted += 1

    if deleted >= batch_size:
        return delete_collection(collection_name, batch_size)

    return deleted

def main():
    print("=" * 60)
    print("구 Firestore 컬렉션 삭제")
    print("=" * 60)
    
    # 삭제할 컬렉션 목록
    old_collections = ['hino_raw', 'hino_draft']
    
    for coll_name in old_collections:
        print(f"\n[{coll_name}] 삭제 시작...")
        
        # 문서 개수 확인
        docs = list(db.collection(coll_name).limit(1).stream())
        if not docs:
            print(f"  ✓ {coll_name}: 이미 비어있음")
            continue
        
        # 삭제 실행
        count = delete_collection(coll_name)
        print(f"  ✅ {coll_name}: {count}개 문서 삭제 완료")
    
    print("\n" + "=" * 60)
    print("삭제 완료!")
    print("=" * 60)
    
    # 최종 확인
    print("\n[최종 확인]")
    for coll_name in old_collections:
        remaining = len(list(db.collection(coll_name).limit(1).stream()))
        print(f"  {coll_name}: {remaining}개 문서")
    
    print("\n[Hierarchical 구조]")
    hierarchical_paths = [
        'projects/hinobalance/raw',
        'projects/hinobalance/draft',
        'projects/hinobalance/final'
    ]
    
    for path in hierarchical_paths:
        parts = path.split('/')
        doc_ref = db.collection(parts[0]).document(parts[1])
        coll_ref = doc_ref.collection(parts[2])
        count = len(list(coll_ref.limit(100).stream()))
        print(f"  {path}: {count}개 문서")

if __name__ == '__main__':
    main()
