"""
기존 Firestore 문서에 doc_type 필드 추가
이론/실전 구분 필드 추가
"""
import firebase_admin
from firebase_admin import credentials, firestore

# Firebase 초기화
if not firebase_admin._apps:
    cred = credentials.Certificate('jnext-service-account.json')
    firebase_admin.initialize_app(cred)

db = firestore.client()

def add_doc_type_field():
    """모든 컬렉션의 문서에 doc_type 필드 추가"""
    collections = ['hino_raw', 'hino_draft', 'hino_final']
    
    for collection_name in collections:
        print(f"\n{'='*70}")
        print(f"📝 {collection_name} 컬렉션 처리 중...")
        print(f"{'='*70}")
        
        docs = db.collection(collection_name).stream()
        count = 0
        
        for doc in docs:
            data = doc.to_dict()
            category = data.get('카테고리') or data.get('category') or ''
            
            # doc_type 결정 (이론 vs 실전)
            if '하이노이론' in category:
                doc_type = "이론"
            else:
                doc_type = "실전"
            
            # doc_type 필드 추가
            doc.reference.update({
                'doc_type': doc_type
            })
            
            count += 1
            print(f"✅ {doc.id}: doc_type={doc_type} (category={category})")
        
        print(f"\n📊 {collection_name}: {count}개 문서 업데이트 완료!")

if __name__ == '__main__':
    print("🚀 doc_type 필드 추가 시작!")
    add_doc_type_field()
    print("\n✅ 모든 문서 업데이트 완료!")
