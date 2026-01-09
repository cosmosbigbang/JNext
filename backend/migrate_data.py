"""
hino_raw_logs → hino_raw 데이터 마이그레이션
기존 데이터를 새 컬렉션으로 이동하고, 원본은 보관
"""
import firebase_admin
from firebase_admin import credentials, firestore
import os
from dotenv import load_dotenv

load_dotenv()

# Firebase 초기화
if not firebase_admin._apps:
    cred = credentials.Certificate(os.getenv('FIREBASE_CREDENTIALS_PATH'))
    firebase_admin.initialize_app(cred)

db = firestore.client()

def migrate_collection():
    """hino_raw_logs → hino_raw 마이그레이션"""
    
    # 1. 기존 hino_raw 초기화 문서 삭제
    print("=== Step 1: 기존 hino_raw 초기화 문서 삭제 ===")
    raw_docs = db.collection('hino_raw').stream()
    for doc in raw_docs:
        doc.reference.delete()
        print(f"❌ 삭제: hino_raw/{doc.id}")
    
    # 2. hino_raw_logs 데이터 복사
    print("\n=== Step 2: hino_raw_logs → hino_raw 복사 ===")
    logs_docs = db.collection('hino_raw_logs').stream()
    migrated_count = 0
    
    for doc in logs_docs:
        data = doc.to_dict()
        # 새 컬렉션에 동일 ID로 복사
        db.collection('hino_raw').document(doc.id).set(data)
        
        # 요약 정보 출력
        category = data.get('카테고리', 'N/A')
        content_preview = data.get('내용', '')[:50]
        print(f"✅ 복사: {doc.id} | {category} | {content_preview}...")
        migrated_count += 1
    
    print(f"\n=== 마이그레이션 완료 ===")
    print(f"총 {migrated_count}개 문서 이동 완료")
    
    # 3. 최종 상태 확인
    print("\n=== 최종 컬렉션 상태 ===")
    collections = ['hino_raw_logs', 'hino_raw', 'hino_draft', 'hino_final']
    for col in collections:
        count = len(list(db.collection(col).stream()))
        print(f"{col}: {count}개 문서")

if __name__ == '__main__':
    print("⚠️  hino_raw_logs → hino_raw 마이그레이션을 시작합니다.")
    print("⚠️  기존 hino_raw의 초기화 문서는 삭제됩니다.\n")
    
    confirm = input("계속하시겠습니까? (yes/no): ")
    if confirm.lower() == 'yes':
        migrate_collection()
        print("\n✅ 마이그레이션 성공!")
        print("💡 hino_raw_logs는 백업용으로 보관됩니다.")
    else:
        print("❌ 마이그레이션 취소")
