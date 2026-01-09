"""
hino_raw_logs 컬렉션 모든 문서 삭제
"""

import requests
import json

API_ENDPOINT = "http://localhost:8000/api/v1/execute/"

# 1. 모든 문서 조회
print("📋 hino_raw_logs 문서 조회 중...")
response = requests.post(
    API_ENDPOINT,
    json={
        "action": "READ",
        "collection": "hino_raw_logs"
    },
    headers={'Content-Type': 'application/json'}
)

result = response.json()
documents = result.get('documents', [])
doc_ids = [doc['id'] for doc in documents]

print(f"현재 문서 수: {len(doc_ids)}")
print(f"문서 IDs: {doc_ids}")

# 2. 모든 문서 삭제
if doc_ids:
    print("\n🗑️ 삭제 시작...")
    for doc_id in doc_ids:
        del_response = requests.post(
            API_ENDPOINT,
            json={
                "action": "DELETE",
                "collection": "hino_raw_logs",
                "document_id": doc_id
            },
            headers={'Content-Type': 'application/json'}
        )
        print(f"   ✅ {doc_id} 삭제 완료")
    
    print(f"\n🎉 총 {len(doc_ids)}개 문서 삭제 완료!")
else:
    print("삭제할 문서가 없습니다.")
