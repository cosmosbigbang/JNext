"""
하이노워밍팔돌리기 전체 검색
"""
from firebase_admin import firestore, credentials
import firebase_admin

if not firebase_admin._apps:
    cred = credentials.Certificate('../jnext-service-account.json')
    firebase_admin.initialize_app(cred)

db = firestore.client()

search_keyword = "하이노워밍팔돌리기"

print('='*60)
print(f'🔍 "{search_keyword}" 검색 결과')
print('='*60)

# 1. projects/hinobalance/raw
print('\n📦 1. projects/hinobalance/raw')
print('-'*60)
raw_docs = db.collection('projects').document('hinobalance').collection('raw').stream()
raw_count = 0
for doc in raw_docs:
    data = doc.to_dict()
    title = data.get('제목', '')
    if search_keyword in title or search_keyword in data.get('원본', ''):
        raw_count += 1
        print(f"{raw_count}. {doc.id}")
        print(f"   제목: {title}")
        print()

if raw_count == 0:
    print("❌ 없음\n")

# 2. hino_raw (구 구조)
print('📦 2. hino_raw (구 컬렉션)')
print('-'*60)
old_raw_docs = db.collection('hino_raw').stream()
old_raw_count = 0
for doc in old_raw_docs:
    data = doc.to_dict()
    title = data.get('제목', '')
    if search_keyword in title or search_keyword in data.get('내용', ''):
        old_raw_count += 1
        print(f"{old_raw_count}. {doc.id}")
        print(f"   제목: {title}")
        print()

if old_raw_count == 0:
    print("❌ 없음\n")

# 3. hino_draft
print('📦 3. hino_draft')
print('-'*60)
draft_docs = db.collection('hino_draft').stream()
draft_count = 0
for doc in draft_docs:
    data = doc.to_dict()
    title = data.get('제목', '')
    if search_keyword in title or search_keyword in data.get('내용', ''):
        draft_count += 1
        print(f"{draft_count}. {doc.id}")
        print(f"   제목: {title}")
        print()

if draft_count == 0:
    print("❌ 없음\n")

# 4. hino_final
print('📦 4. hino_final')
print('-'*60)
final_docs = db.collection('hino_final').stream()
final_count = 0
for doc in final_docs:
    data = doc.to_dict()
    title = data.get('제목', '')
    if search_keyword in title or search_keyword in data.get('내용', ''):
        final_count += 1
        print(f"{final_count}. {doc.id}")
        print(f"   제목: {title}")
        print()

if final_count == 0:
    print("❌ 없음\n")

# 요약
print('='*60)
print('📊 요약')
print('='*60)
print(f"projects/hinobalance/raw: {raw_count}개")
print(f"hino_raw (구): {old_raw_count}개")
print(f"hino_draft: {draft_count}개")
print(f"hino_final: {final_count}개")
print(f"\n총 {raw_count + old_raw_count + draft_count + final_count}개")
