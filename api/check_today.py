"""
오늘(2026-01-14) Firestore 메시지 확인
"""
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime, timezone, timedelta

# Firebase 초기화
if not firebase_admin._apps:
    cred = credentials.Certificate('../jnext-service-account.json')
    firebase_admin.initialize_app(cred)

db = firestore.client()
KST = timezone(timedelta(hours=9))

# 오늘 날짜 시작 시간 (2026-01-14 00:00:00 KST)
today_start = datetime(2026, 1, 14, 0, 0, 0, tzinfo=KST)

print(f"📅 {today_start.date()} 이후 메시지 검색 중...")
print("=" * 80)

# 전체 메시지 가져와서 Python에서 필터링 (한글 필드명 때문)
all_docs = list(db.collection('chat_history').stream())
docs = [d for d in all_docs if d.to_dict().get('시간', '') >= today_start]

print(f"\n✅ 전체 {len(all_docs)}개 중 오늘 {len(docs)}개 메시지 발견\n")

if docs:
    # 시간순 정렬
    sorted_docs = sorted(docs, key=lambda x: x.to_dict().get('시간', ''), reverse=True)
    
    for idx, doc in enumerate(sorted_docs, 1):
        data = doc.to_dict()
        시간 = data.get('시간', '')
        역할 = data.get('역할', '')
        모드 = data.get('모드', '')
        모델 = data.get('모델', '')
        내용 = data.get('내용', '')
        
        print(f"{idx}. [{시간}]")
        print(f"   역할: {역할} | 모드: {모드} | 모델: {모델}")
        print(f"   내용: {내용[:100]}{'...' if len(내용) > 100 else ''}")
        print("-" * 80)
else:
    print("❌ 오늘 날짜 메시지가 없습니다!")
    print("\n💡 확인 사항:")
    print("  1. views_v2.py에서 save_chat_history()가 호출되는가?")
    print("  2. now_kst() 함수가 올바른 시간을 반환하는가?")
    print("  3. Django 서버 로그에 저장 에러가 있는가?")
