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

# 모든 컬렉션 검색
collections = ['hino_raw', 'hino_draft', 'hino_final']
found_data = []

for collection_name in collections:
    docs = db.collection(collection_name).stream()
    for doc in docs:
        doc_data = doc.to_dict()
        for field, value in doc_data.items():
            if isinstance(value, str):
                if '하이노밸런스' in value or 'balance' in value.lower() or 'hino' in value.lower():
                    found_data.append({
                        'collection': collection_name,
                        'doc_id': doc.id,
                        'field': field,
                        'value': value
                    })

if found_data:
    print(f"✅ 관련 데이터 {len(found_data)}건 발견:\n")
    for item in found_data:
        print(f"📁 {item['collection']}/{item['doc_id']}")
        print(f"   📝 {item['field']}: {item['value']}\n")
else:
    print("❌ '하이노밸런스' 관련 데이터 없음\n")
    print("현재 DB 상태:")
    for collection_name in collections:
        count = len(list(db.collection(collection_name).stream()))
        print(f"  - {collection_name}: {count}개 문서")
