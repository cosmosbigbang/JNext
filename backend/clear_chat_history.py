"""
Firestore chat_history 전체 삭제
"""
import firebase_admin
from firebase_admin import credentials, firestore

# Firebase 초기화
if not firebase_admin._apps:
    cred = credentials.Certificate('../jnext-service-account.json')
    firebase_admin.initialize_app(cred)

db = firestore.client()

print("🗑️  chat_history 컬렉션 전체 삭제 중...")
print("=" * 80)

# 전체 문서 가져오기
docs = db.collection('chat_history').stream()

count = 0
for doc in docs:
    doc.reference.delete()
    count += 1
    if count % 10 == 0:
        print(f"  삭제 중... {count}개")

print("=" * 80)
print(f"✅ 총 {count}개 문서 삭제 완료!")
print("\n새로운 ID 형식(YYYYMMDD_HHMMSS_microseconds)으로 다시 시작합니다.")
