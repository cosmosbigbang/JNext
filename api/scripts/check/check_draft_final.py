"""
하이노워밍팔돌리기 - draft, final 컬렉션 확인
"""
from firebase_admin import firestore, credentials
import firebase_admin

if not firebase_admin._apps:
    cred = credentials.Certificate('../jnext-service-account.json')
    firebase_admin.initialize_app(cred)

db = firestore.client()

search_keyword = "하이노워밍팔돌리기"

print('='*60)
print(f'🔍 "{search_keyword}" - draft/final 검색')
print('='*60)

# 1. hino_draft
print('\n📦 hino_draft')
print('-'*60)
draft_docs = db.collection('hino_draft').stream()
draft_count = 0
for doc in draft_docs:
    data = doc.to_dict()
    title = data.get('제목', '')
    content = data.get('내용', '') or data.get('전체글', '')
    
    if search_keyword in title or search_keyword in content:
        draft_count += 1
        print(f"{draft_count}. ID: {doc.id}")
        print(f"   제목: {title}")
        print(f"   생성: {data.get('생성일시', 'N/A')}")
        print()

print(f"✅ draft 총 {draft_count}개\n")

# 2. hino_final
print('📦 hino_final')
print('-'*60)
final_docs = db.collection('hino_final').stream()
final_count = 0
for doc in final_docs:
    data = doc.to_dict()
    title = data.get('제목', '')
    content = data.get('내용', '') or data.get('전체글', '')
    
    if search_keyword in title or search_keyword in content:
        final_count += 1
        print(f"{final_count}. ID: {doc.id}")
        print(f"   제목: {title}")
        print(f"   생성: {data.get('생성일시', 'N/A')}")
        print()

print(f"✅ final 총 {final_count}개\n")

# 3. projects/hinobalance/raw (참고)
print('📦 projects/hinobalance/raw (참고)')
print('-'*60)
raw_docs = db.collection('projects').document('hinobalance').collection('raw').stream()
raw_count = 0
for doc in raw_docs:
    data = doc.to_dict()
    title = data.get('제목', '')
    
    if search_keyword in title or search_keyword in data.get('원본', ''):
        raw_count += 1

print(f"✅ raw 총 {raw_count}개\n")

print('='*60)
print('📊 요약')
print('='*60)
print(f"hino_draft: {draft_count}개")
print(f"hino_final: {final_count}개")
print(f"projects/.../raw: {raw_count}개")
print()
print("❗ J님이 보시는 2개는 draft나 final에 있는 것으로 추정됩니다.")
