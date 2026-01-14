"""
Firestore hino_draft 컬렉션의 마크다운 강조(**텍스트**) 제거
전자책 출판용 - 가시성 개선
"""
import os
import firebase_admin
from firebase_admin import credentials, firestore
import re
from datetime import datetime
from dotenv import load_dotenv

# .env 로드
load_dotenv()

# Firebase 초기화
if not firebase_admin._apps:
    cred_path = os.getenv('FIREBASE_CREDENTIALS_PATH', '../jnext-service-account.json')
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)

def remove_markdown_bold():
    """모든 draft 문서에서 **강조** 제거"""
    db = firestore.client()
    
    # hino_draft 컬렉션 조회
    docs = db.collection('hino_draft').stream()
    
    updated_count = 0
    total_count = 0
    
    for doc in docs:
        total_count += 1
        data = doc.to_dict()
        doc_id = doc.id
        
        modified = False
        updates = {}
        
        # '내용' 필드 처리
        if '내용' in data and data['내용']:
            original = data['내용']
            # **텍스트** → 텍스트
            cleaned = re.sub(r'\*\*([^*]+)\*\*', r'\1', original)
            if cleaned != original:
                updates['내용'] = cleaned
                modified = True
        
        # '전체글' 필드 처리
        if '전체글' in data and data['전체글']:
            original = data['전체글']
            # **텍스트** → 텍스트
            cleaned = re.sub(r'\*\*([^*]+)\*\*', r'\1', original)
            if cleaned != original:
                updates['전체글'] = cleaned
                modified = True
        
        # 수정사항이 있으면 업데이트
        if modified:
            updates['수정일시'] = firestore.SERVER_TIMESTAMP
            db.collection('hino_draft').document(doc_id).update(updates)
            updated_count += 1
            print(f"✅ [{updated_count}] {data.get('제목', doc_id)[:30]}... 업데이트")
    
    print(f"\n{'='*60}")
    print(f"🎉 완료!")
    print(f"- 총 문서: {total_count}개")
    print(f"- 업데이트: {updated_count}개")
    print(f"- 건너뜀: {total_count - updated_count}개")
    print(f"{'='*60}")

if __name__ == '__main__':
    print("🚀 마크다운 강조 제거 시작...")
    print("컬렉션: hino_draft")
    print("패턴: **텍스트** → 텍스트")
    print()
    
    remove_markdown_bold()
