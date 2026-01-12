"""
Draft 컬렉션 샘플 확인 - 강조 패턴 찾기
"""
import os
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv

load_dotenv()

if not firebase_admin._apps:
    cred_path = os.getenv('FIREBASE_CREDENTIALS_PATH', '../jnext-service-account.json')
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)

db = firestore.client()
docs = db.collection('hino_draft').limit(3).stream()

print("=" * 80)
print("샘플 문서 확인 (첫 3개)")
print("=" * 80)

for doc in docs:
    data = doc.to_dict()
    print(f"\n📄 제목: {data.get('제목', doc.id)}")
    
    content = data.get('내용', '')[:500]
    print(f"\n내용 샘플 (500자):")
    print(content)
    print("\n" + "-" * 80)
    
    # ** 패턴 찾기
    import re
    bold_patterns = re.findall(r'\*\*[^*]+\*\*', content)
    if bold_patterns:
        print(f"✅ 발견된 **강조** 패턴: {len(bold_patterns)}개")
        for i, pattern in enumerate(bold_patterns[:5], 1):
            print(f"  {i}. {pattern}")
    else:
        print("❌ **강조** 패턴 없음")
