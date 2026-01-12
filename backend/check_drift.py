"""
drift 컬렉션 내용 확인 및 굵게 강조 분석
"""
import firebase_admin
from firebase_admin import credentials, firestore
import os
from pathlib import Path

# Firebase 초기화
if not firebase_admin._apps:
    base_dir = Path(__file__).resolve().parent
    cred_path = base_dir / 'jnext-service-account.json'
    cred = credentials.Certificate(str(cred_path))
    firebase_admin.initialize_app(cred)

db = firestore.client()

print("=" * 80)
print("HINO_DRIFT 컬렉션 내용 분석")
print("=" * 80)

# hino_drift 컬렉션 조회
drift_ref = db.collection('hino_drift')
docs = drift_ref.stream()

doc_count = 0
for doc in docs:
    doc_count += 1
    data = doc.to_dict()
    
    print(f"\n{'=' * 80}")
    print(f"문서 ID: {doc.id}")
    print(f"{'=' * 80}")
    
    # 모든 필드 출력
    for field, value in data.items():
        if isinstance(value, str):
            # ** ** 사용 횟수 계산
            bold_count = value.count('**') // 2
            
            print(f"\n[{field}]")
            print(f"  굵게 사용 횟수: {bold_count}회")
            print(f"  내용 길이: {len(value)}자")
            
            # 내용 미리보기 (처음 200자)
            preview = value[:200] + "..." if len(value) > 200 else value
            print(f"  미리보기: {preview}")
        else:
            print(f"\n[{field}]: {value}")

print(f"\n{'=' * 80}")
print(f"총 문서 수: {doc_count}개")
print(f"{'=' * 80}")
