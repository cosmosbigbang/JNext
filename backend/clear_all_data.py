"""
Firestore 전체 데이터 삭제 스크립트
"""
import firebase_admin
from firebase_admin import credentials, firestore
import os
from pathlib import Path

# Firebase 초기화
if not firebase_admin._apps:
    # settings.py와 동일한 경로 찾기 로직
    BASE_DIR = Path(__file__).resolve().parent
    
    jnext_root_path = BASE_DIR.parent / 'jnext-service-account.json'
    backend_path = BASE_DIR / 'jnext-service-account.json'
    
    if jnext_root_path.exists():
        firebase_cred_path = jnext_root_path
    elif backend_path.exists():
        firebase_cred_path = backend_path
    else:
        firebase_cred_path = jnext_root_path  # 기본값
    
    cred = credentials.Certificate(str(firebase_cred_path))
    firebase_admin.initialize_app(cred)

db = firestore.client()

def delete_collection(collection_name):
    """컬렉션 전체 삭제"""
    docs = db.collection(collection_name).stream()
    deleted = 0
    
    for doc in docs:
        doc.reference.delete()
        deleted += 1
    
    return deleted

# 모든 컬렉션 조회
collections = db.collections()

print("🗑️  Firestore 전체 데이터 삭제 시작...\n")

total_deleted = 0
for collection in collections:
    col_name = collection.id
    deleted = delete_collection(col_name)
    total_deleted += deleted
    print(f"✅ {col_name}: {deleted}개 문서 삭제")

print(f"\n✅ 총 {total_deleted}개 문서 삭제 완료!")
print("🎉 Firestore가 깨끗해졌습니다!")
