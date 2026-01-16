"""
하이노이론 25개 문서 통합 스크립트
"""
import sys
import os
from pathlib import Path
import firebase_admin
from firebase_admin import credentials, firestore

# 인코딩 설정
sys.stdout.reconfigure(encoding='utf-8')

# Firebase 초기화
if not firebase_admin._apps:
    cred = credentials.Certificate('jnext-service-account.json')
    firebase_admin.initialize_app(cred)

db = firestore.client()

def get_theory_docs():
    """하이노이론 카테고리의 모든 문서 가져오기"""
    print("\n" + "="*70)
    print("하이노이론 25개 문서 수집 중...")
    print("="*70 + "\n")
    
    docs = db.collection('hino_raw').where('category', '==', '하이노이론').stream()
    
    results = []
    for doc in docs:
        data = doc.to_dict()
        results.append({
            'id': doc.id,
            'exercise_name': data.get('exercise_name', ''),
            'content': data.get('content', '')
        })
        print(f"✓ {data.get('exercise_name', doc.id)}")
    
    print(f"\n총 {len(results)}개 문서 수집 완료!\n")
    return results

if __name__ == '__main__':
    docs = get_theory_docs()
    
    # 전체 내용 하나로 합치기
    print("="*70)
    print("통합 작업 준비...")
    print("="*70 + "\n")
    
    combined_content = ""
    for i, doc in enumerate(docs, 1):
        combined_content += f"\n\n### [{i}] {doc['exercise_name']} ###\n\n"
        combined_content += doc['content']
        combined_content += "\n\n" + "-"*70
    
    # 파일로 저장
    with open('theory_combined.txt', 'w', encoding='utf-8') as f:
        f.write(combined_content)
    
    print(f"✅ theory_combined.txt 저장 완료!")
    print(f"   총 길이: {len(combined_content):,} 자")
    print(f"\n다음 단계: 이 내용을 바탕으로 통합 이론 작성")
