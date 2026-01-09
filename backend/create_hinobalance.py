"""
하이노밸런스 라이브러리 데이터 생성
"""

import requests
import json

API_ENDPOINT = "http://localhost:8000/api/v1/execute/"

data = {
    "action": "CREATE",
    "collection": "hinobalance_library",
    "payload": {
        "type": "이론",
        "category": "하이노워킹",
        "title": "중심이동의 3원칙: 풋샵과 골반의 조화",
        "content": "걸음의 시작은 발바닥 전체의 압력 분산(풋샵)에서 시작되어, 골반의 부드러운 회전을 통해 반대쪽 발로 체중이 이동될 때 완성됩니다. 이는 단순히 걷는 것이 아니라 전신 코어를 활성화하는 과정입니다.",
        "difficulty": "Lv.2 (보통)",
        "effect": "코어 근육 활성화, 골반 불균형 교정, 보행 효율 개선",
        "target": "바른 자세를 원하는 직장인, 보행 교정이 필요한 고령층",
        "rating": 5.0,
        "keywords": ["#하이노워킹", "#중심이동", "#코어운동", "#골반교정"],
        "updated_at": "2026-01-04T18:25:00"
    }
}

response = requests.post(API_ENDPOINT, json=data)
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

if response.status_code == 200:
    print("\n✅ 데이터 생성 성공!")
    print(f"문서 ID: {response.json()['document_id']}")
