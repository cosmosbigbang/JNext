"""
DB 정리 스크립트
1. hino_raw_logs 삭제 (백업 완료)
2. hino_draft/final 초기화 문서 삭제
"""
import firebase_admin
from firebase_admin import credentials, firestore
import os
from dotenv import load_dotenv

load_dotenv()

if not firebase_admin._apps:
    cred = credentials.Certificate(os.getenv('FIREBASE_CREDENTIALS_PATH'))
    firebase_admin.initialize_app(cred)

db = firestore.client()

def cleanup_database():
    """불필요한 데이터 정리"""
    
    print("=== Step 1: hino_raw_logs 삭제 (백업 완료, 중복 제거) ===")
    logs_docs = list(db.collection('hino_raw_logs').stream())
    for doc in logs_docs:
        doc.reference.delete()
        print(f"❌ 삭제: hino_raw_logs/{doc.id}")
    print(f"✅ {len(logs_docs)}개 문서 삭제 완료\n")
    
    print("=== Step 2: hino_draft/final 초기화 문서 삭제 ===")
    draft_docs = list(db.collection('hino_draft').stream())
    for doc in draft_docs:
        data = doc.to_dict()
        if '초기화 완료' in data.get('내용', ''):
            doc.reference.delete()
            print(f"❌ 삭제: hino_draft/{doc.id}")
    
    final_docs = list(db.collection('hino_final').stream())
    for doc in final_docs:
        data = doc.to_dict()
        if '초기화 완료' in data.get('내용', ''):
            doc.reference.delete()
            print(f"❌ 삭제: hino_final/{doc.id}")
    
    print("\n=== 최종 상태 ===")
    collections = ['hino_raw_logs', 'hino_raw', 'hino_draft', 'hino_final']
    for col in collections:
        count = len(list(db.collection(col).stream()))
        print(f"{col}: {count}개 문서")

if __name__ == '__main__':
    print("⚠️  불필요한 데이터를 정리합니다.")
    print("⚠️  hino_raw_logs (백업용 중복) 삭제")
    print("⚠️  hino_draft/final 초기화 문서 삭제\n")
    
    confirm = input("계속하시겠습니까? (yes/no): ")
    if confirm.lower() == 'yes':
        cleanup_database()
        print("\n✅ 정리 완료!")
    else:
        print("❌ 정리 취소")
