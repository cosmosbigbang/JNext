"""
Firestore hinobalance RAW 컬렉션 확인
"""
from firebase_admin import firestore, credentials
import firebase_admin

if not firebase_admin._apps:
    cred = credentials.Certificate('../jnext-service-account.json')
    firebase_admin.initialize_app(cred)

db = firestore.client()

# projects/hinobalance/raw 확인
docs = db.collection('projects').document('hinobalance').collection('raw').limit(10).stream()

print('='*60)
print('📦 projects/hinobalance/raw 문서 목록')
print('='*60)

count = 0
for doc in docs:
    data = doc.to_dict()
    count += 1
    print(f"{count}. ID: {doc.id}")
    print(f"   제목: {data.get('제목', '제목없음')}")
    print(f"   카테고리: {data.get('category', '미분류')}")
    print(f"   품질점수: {data.get('품질점수', 'N/A')}")
    print()

if count == 0:
    print("❌ 문서 없음!")
    print("\n확인사항:")
    print("1. project_id가 'hinobalance'로 전달되었나?")
    print("2. evaluate_chat_value()가 True 반환했나?")
    print("3. analyze_and_save_raw()에서 에러 발생했나?")
else:
    print(f"✅ 총 {count}개 문서 발견")
