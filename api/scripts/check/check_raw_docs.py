import firebase_admin
from firebase_admin import credentials, firestore
from pathlib import Path

# Firebase 초기화
if not firebase_admin._apps:
    base_dir = Path(__file__).resolve().parent
    cred_path = base_dir.parent / 'jnext-service-account.json'
    cred = credentials.Certificate(str(cred_path))
    firebase_admin.initialize_app(cred)

db = firestore.client()

# 최근 RAW 문서 10개 조회
docs = db.collection('projects').document('hinobalance').collection('raw').order_by('timestamp', direction=firestore.Query.DESCENDING).limit(10).stream()

print('\n=== 최근 RAW 문서 10개 ===')
for i, doc in enumerate(docs):
    data = doc.to_dict()
    print(f'{i+1}. ID: {doc.id}')
    print(f'   제목: {data.get("제목", "없음")}')
    print(f'   원본: {data.get("원본", "")[:80]}...')
    print(f'   키워드: {data.get("키워드", [])}')
    print(f'   시간: {data.get("timestamp")}')
    print()

# "하이노풋삽벽두손" 포함된 문서만 필터
print('\n=== "풋삽" 포함 문서 ===')
all_docs = db.collection('projects').document('hinobalance').collection('raw').stream()
footsab_docs = [doc for doc in all_docs if '풋삽' in doc.to_dict().get('제목', '') or '풋삽' in doc.to_dict().get('원본', '')]

for i, doc in enumerate(footsab_docs):
    data = doc.to_dict()
    print(f'{i+1}. 제목: {data.get("제목", "없음")}')
    print(f'   원본: {data.get("원본", "")[:100]}...')
    print()

print(f'\n총 {len(footsab_docs)}개 문서 발견')
