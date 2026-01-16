"""
간단한 DB 조회 스크립트 (Django 서버 필요 없음)
"""
from google.cloud import firestore
import os
import json

# 서비스 계정 설정
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'C:/Projects/JNext/jnext-service-account.json'

db = firestore.client()

print("=" * 80)
print("하이노밸런스 DB 전체 분석")
print("=" * 80)

collections = ['raw', 'draft', 'final']
all_docs = {}

for col in collections:
    print(f"\n[{col.upper()}] 분석 중...")
    docs_ref = db.collection('projects').document('hinobalance').collection(col)
    docs = list(docs_ref.limit(100).stream())
    all_docs[col] = docs
    print(f"  → {len(docs)}개 발견")

# 카테고리별 분류
print("\n" + "=" * 80)
print("📊 카테고리별 문서 목록")
print("=" * 80)

categories = {}

for col, docs in all_docs.items():
    for doc in docs:
        data = doc.to_dict()
        category = data.get('카테고리') or data.get('category') or '미분류'
        title = (data.get('제목') or data.get('title') or 
                data.get('exercise_name') or doc.id)
        
        if category not in categories:
            categories[category] = {}
        if col not in categories[category]:
            categories[category][col] = []
        
        categories[category][col].append({
            'id': doc.id,
            'title': title,
            'has_content': bool(data.get('내용') or data.get('content') or data.get('ai_응답')),
            'has_original': bool(data.get('J님원본') or data.get('원본')),
            'keywords': data.get('키워드', ''),
            'quality': data.get('품질점수', 0)
        })

# 출력
for cat in sorted(categories.keys()):
    print(f"\n【{cat}】")
    for col in ['raw', 'draft', 'final']:
        if col in categories[cat]:
            docs = categories[cat][col]
            print(f"  [{col.upper()}] {len(docs)}개")
            for d in docs[:10]:  # 최대 10개만
                status = "✅" if d['has_content'] else "⚠️"
                original = "📝" if d['has_original'] else "  "
                quality = f"★{d['quality']}" if d['quality'] > 0 else ""
                print(f"    {status}{original} {d['title'][:40]} {quality}")

# 통계
print("\n" + "=" * 80)
print("📈 통계")
print("=" * 80)
total = sum(len(docs) for docs in all_docs.values())
print(f"총 문서: {total}개")
print(f"  RAW: {len(all_docs['raw'])}개")
print(f"  DRAFT: {len(all_docs['draft'])}개")
print(f"  FINAL: {len(all_docs['final'])}개")
print(f"\n카테고리: {len(categories)}개")

# 샘플 내용
print("\n" + "=" * 80)
print("📄 샘플 문서 상세 (DRAFT 첫 번째)")
print("=" * 80)

if all_docs['draft']:
    sample_doc = all_docs['draft'][0]
    sample_data = sample_doc.to_dict()
    
    print(f"문서 ID: {sample_doc.id}")
    print(f"제목: {sample_data.get('제목') or sample_data.get('title', 'N/A')}")
    print(f"카테고리: {sample_data.get('카테고리', 'N/A')}")
    print(f"\n전체 필드:")
    for key in sorted(sample_data.keys()):
        value = sample_data[key]
        if isinstance(value, str):
            value = value[:50] + "..." if len(value) > 50 else value
        print(f"  {key}: {value}")

print("\n" + "=" * 80)
print("완료!")
print("=" * 80)
