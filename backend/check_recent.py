import firebase_admin
from firebase_admin import credentials, firestore
import json

# Firebase 초기화
try:
    cred = credentials.Certificate('jnext-service-account.json')
    firebase_admin.initialize_app(cred)
except:
    pass

db = firestore.client()

# 최근 저장된 문서 조회 (hino_draft)
print("=== 최근 저장된 문서 (hino_draft) ===\n")
docs = db.collection('hino_draft').limit(5).stream()

for idx, doc in enumerate(docs, 1):
    data = doc.to_dict()
    print(f"--- 문서 {idx} ---")
    print(f"제목: {data.get('제목', 'N/A')}")
    print(f"카테고리: {data.get('카테고리', 'N/A')}")
    print(f"작성일시: {data.get('작성일시', 'N/A')}")
    print(f"내용 길이: {len(data.get('내용', ''))}자")
    print(f"내용 미리보기:\n{data.get('내용', '')[:300]}...")
    print()
