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

# hino_raw_logs 데이터 확인
print("=== hino_raw_logs 컬렉션 데이터 ===\n")
docs = db.collection('hino_raw_logs').stream()
doc_list = list(docs)

if not doc_list:
    print("❌ hino_raw_logs 컬렉션이 비어있습니다.")
else:
    print(f"✅ 총 {len(doc_list)}개 문서 발견\n")
    for idx, doc in enumerate(doc_list, 1):
        print(f"[{idx}] 📁 {doc.id}")
        data = doc.to_dict()
        for key, value in data.items():
            if isinstance(value, str) and len(value) > 100:
                print(f"   {key}: {value[:100]}...")
            else:
                print(f"   {key}: {value}")
        print()

# 현재 컬렉션 상태 비교
print("\n=== 현재 컬렉션 상태 비교 ===")
collections = ['hino_raw_logs', 'hino_raw', 'hino_draft', 'hino_final']
for col in collections:
    count = len(list(db.collection(col).stream()))
    print(f"{col}: {count}개 문서")
