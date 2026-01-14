"""
hino_draft 컬렉션의 굵게 강조(**) 사용 분석 및 수정
"""
import firebase_admin
from firebase_admin import credentials, firestore
from pathlib import Path
import re

# Firebase 초기화
if not firebase_admin._apps:
    base_dir = Path(__file__).resolve().parent
    cred_path = base_dir / 'jnext-service-account.json'
    cred = credentials.Certificate(str(cred_path))
    firebase_admin.initialize_app(cred)

db = firestore.client()

print("=" * 80)
print("HINO_DRAFT 컬렉션 - 굵게 강조 분석")
print("=" * 80)

# hino_draft 컬렉션 조회
draft_ref = db.collection('hino_draft')
docs = draft_ref.order_by('created_at').stream()

doc_count = 0
total_bold_count = 0

for doc in docs:
    doc_count += 1
    data = doc.to_dict()
    
    print(f"\n{'=' * 80}")
    print(f"문서 #{doc_count}: {doc.id}")
    print(f"{'=' * 80}")
    
    # content 필드 분석
    if 'content' in data and isinstance(data['content'], str):
        content = data['content']
        
        # ** ** 사용 횟수 계산
        bold_matches = re.findall(r'\*\*([^*]+?)\*\*', content)
        bold_count = len(bold_matches)
        total_bold_count += bold_count
        
        print(f"카테고리: {data.get('category', 'N/A')}")
        print(f"콘텐츠 타입: {data.get('content_type', 'N/A')}")
        print(f"전체 길이: {len(content):,}자")
        print(f"굵게 사용: {bold_count}회")
        
        if bold_count > 0:
            print(f"\n[굵게 처리된 텍스트]")
            for i, text in enumerate(bold_matches[:10], 1):  # 처음 10개만
                print(f"  {i}. {text[:50]}...")
            
            if bold_count > 10:
                print(f"  ... 외 {bold_count - 10}개 더")
        
        # 내용 미리보기 (처음 300자)
        preview = content[:300].replace('\n', ' ')
        print(f"\n[내용 미리보기]")
        print(f"  {preview}...")
    
    # 기타 필드 정보
    print(f"\n[메타 정보]")
    print(f"  생성일: {data.get('created_at', 'N/A')}")
    print(f"  상태: {data.get('status', 'N/A')}")
    if 'exercise_names' in data:
        print(f"  운동: {data.get('exercise_names', [])}")

print(f"\n{'=' * 80}")
print(f"총 문서 수: {doc_count}개")
print(f"총 굵게 사용 횟수: {total_bold_count}회")
print(f"문서당 평균: {total_bold_count / doc_count if doc_count > 0 else 0:.1f}회")
print(f"{'=' * 80}")
