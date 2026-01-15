"""
하이노밸런스 DB 전체 분석 스크립트
"""
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from google.cloud import firestore
import json
from collections import defaultdict

db = firestore.client()

print("=" * 80)
print("하이노밸런스 DB 전체 분석")
print("=" * 80)

# 모든 컬렉션 조회
collections = ['raw', 'draft', 'final']
all_data = defaultdict(list)

for collection in collections:
    print(f"\n[{collection.upper()}] 컬렉션 분석 중...")
    docs_ref = db.collection('projects').document('hinobalance').collection(collection)
    docs = docs_ref.stream()
    
    count = 0
    for doc in docs:
        data = doc.to_dict()
        data['doc_id'] = doc.id
        all_data[collection].append(data)
        count += 1
    
    print(f"  → {count}개 문서 발견")

# 상세 분석
print("\n" + "=" * 80)
print("📊 카테고리별 분류")
print("=" * 80)

categories = defaultdict(lambda: defaultdict(list))

for collection, docs in all_data.items():
    for doc in docs:
        category = doc.get('카테고리') or doc.get('category') or '미분류'
        title = (doc.get('제목') or doc.get('title') or 
                doc.get('exercise_name') or doc.get('doc_id') or 'Unknown')
        
        categories[category][collection].append({
            'doc_id': doc['doc_id'],
            'title': title,
            'has_content': bool(doc.get('내용') or doc.get('content') or doc.get('ai_응답')),
            'has_original': bool(doc.get('J님원본') or doc.get('원본')),
            'quality': doc.get('품질점수', 0)
        })

# 카테고리별 출력
for category in sorted(categories.keys()):
    print(f"\n【{category}】")
    for collection in collections:
        docs = categories[category][collection]
        if docs:
            print(f"  [{collection.upper()}] {len(docs)}개")
            for d in docs:
                status = "✅" if d['has_content'] else "⚠️"
                original = "📝" if d['has_original'] else "  "
                print(f"    {status} {original} {d['title']} (품질: {d['quality']})")

# 전체 통계
print("\n" + "=" * 80)
print("📈 전체 통계")
print("=" * 80)
print(f"총 문서 수: {sum(len(docs) for docs in all_data.values())}개")
print(f"  - RAW: {len(all_data['raw'])}개")
print(f"  - DRAFT: {len(all_data['draft'])}개")
print(f"  - FINAL: {len(all_data['final'])}개")
print(f"\n카테고리 수: {len(categories)}개")
for cat in sorted(categories.keys()):
    total = sum(len(categories[cat][col]) for col in collections)
    print(f"  - {cat}: {total}개")

# 상세 내용 샘플
print("\n" + "=" * 80)
print("📄 샘플 문서 내용 (DRAFT 1개)")
print("=" * 80)

if all_data['draft']:
    sample = all_data['draft'][0]
    print(f"문서 ID: {sample['doc_id']}")
    print(f"제목: {sample.get('제목') or sample.get('title') or 'N/A'}")
    print(f"카테고리: {sample.get('카테고리') or 'N/A'}")
    print(f"\n필드 목록:")
    for key in sorted(sample.keys()):
        if key not in ['doc_id', '내용', 'content', 'ai_응답', 'J님원본', '원본']:
            value = sample[key]
            if isinstance(value, str) and len(value) > 50:
                value = value[:50] + "..."
            print(f"  - {key}: {value}")
    
    # 내용 샘플
    content = (sample.get('내용') or sample.get('content') or 
              sample.get('ai_응답') or sample.get('정리본') or '')
    if content:
        print(f"\n내용 샘플 (첫 300자):")
        print(content[:300] + "...")

print("\n" + "=" * 80)
print("분석 완료!")
print("=" * 80)
