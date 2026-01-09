"""
3단계 컬렉션 구조 초기화
- hino_raw: RAW 원본/아이디어
- hino_draft: DRAFT 정리 중
- hino_final: FINAL 최종 배포
"""

import requests
import json
from datetime import datetime

API_ENDPOINT = "http://localhost:8000/api/v1/execute/"

# 1. hino_raw 초기 데이터
raw_data = {
    "action": "CREATE",
    "collection": "hino_raw",
    "payload": {
        "종류": "시스템",
        "카테고리": "초기화",
        "내용": "hino_raw 컬렉션 초기화 완료. RAW 원본 데이터 저장용.",
        "데이터상태": "RAW",
        "타임스탬프": datetime.now().isoformat(),
        "기타": "3단계 컬렉션 구조 적용"
    }
}

# 2. hino_draft 초기 데이터
draft_data = {
    "action": "CREATE",
    "collection": "hino_draft",
    "payload": {
        "제목": "초기화 문서",
        "내용": "hino_draft 컬렉션 초기화 완료. 정리 중인 초안 저장용.",
        "데이터상태": "DRAFT",
        "원본참조": [],
        "작성일": datetime.now().isoformat(),
        "승인여부": False
    }
}

# 3. hino_final 초기 데이터
final_data = {
    "action": "CREATE",
    "collection": "hino_final",
    "payload": {
        "제목": "초기화 문서",
        "내용": "hino_final 컬렉션 초기화 완료. 최종 배포용 콘텐츠 저장용.",
        "데이터상태": "FINAL",
        "버전": "v1.0",
        "원본참조": [],
        "초안참조": "",
        "승인일": datetime.now().isoformat(),
        "배포처": []
    }
}

print("=" * 60)
print("🚀 3단계 컬렉션 구조 초기화 시작...")
print("=" * 60)

datasets = [
    ("hino_raw", raw_data),
    ("hino_draft", draft_data),
    ("hino_final", final_data)
]

for collection_name, data in datasets:
    try:
        print(f"\n📦 {collection_name} 생성 중...")
        response = requests.post(
            API_ENDPOINT,
            json=data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            result = response.json()
            doc_id = result.get('document_id', 'N/A')
            print(f"   ✅ 성공! 문서 ID: {doc_id}")
        else:
            print(f"   ❌ 실패 (Status: {response.status_code})")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   ❌ 오류: {str(e)}")

print("\n" + "=" * 60)
print("🎉 3단계 컬렉션 구조 초기화 완료!")
print("=" * 60)
print("\n📊 컬렉션 구조:")
print("   - hino_raw: RAW 원본/아이디어")
print("   - hino_draft: DRAFT 정리 중")
print("   - hino_final: FINAL 최종 배포")
print("\n📝 기존 hino_raw_logs (24개)는 보관용으로 유지됩니다.")
