"""
Firestore chat_history 확인 스크립트 (v2용)
"""
import firebase_admin
from firebase_admin import credentials, firestore
import os
from pathlib import Path

# Firebase 초기화
if not firebase_admin._apps:
    cred_path = Path(__file__).parent.parent / 'jnext-service-account.json'
    cred = credentials.Certificate(str(cred_path))
    firebase_admin.initialize_app(cred)

db = firestore.client()

print('=' * 80)
print('📋 Firestore chat_history 확인 (최근 10개)')
print('=' * 80)

# 최근 대화 조회
docs = db.collection('chat_history').stream()
all_docs = []

for doc in docs:
    data = doc.to_dict()
    data['_id'] = doc.id
    all_docs.append(data)

if not all_docs:
    print('\n❌ chat_history 컬렉션이 비어있습니다!')
    print('   → v2 API 테스트 메시지를 보내보세요.')
else:
    # 시간순 정렬 (최신 → 오래된)
    sorted_docs = sorted(all_docs, key=lambda x: x.get('시간', ''), reverse=True)[:10]
    
    print(f'\n✅ 총 {len(all_docs)}개 대화 중 최근 10개:')
    print('-' * 80)
    
    for i, doc in enumerate(sorted_docs, 1):
        역할 = doc.get('역할', '')
        시간 = doc.get('시간', '')
        모드 = doc.get('모드', '')
        모델 = doc.get('모델', '')
        내용 = doc.get('내용', '')
        
        print(f'\n{i}. [{시간}]')
        print(f'   역할: {역할} | 모드: {모드} | 모델: {모델}')
        
        if len(내용) > 150:
            print(f'   내용: {내용[:150]}...')
        else:
            print(f'   내용: {내용}')

print('\n' + '=' * 80)
