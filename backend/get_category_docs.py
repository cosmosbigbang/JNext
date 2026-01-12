"""
Firestore에서 카테고리별 문서 가져오기
"""
import firebase_admin
from firebase_admin import credentials, firestore

# Firebase 초기화
if not firebase_admin._apps:
    cred = credentials.Certificate('jnext-service-account.json')
    firebase_admin.initialize_app(cred)

db = firestore.client()

def get_category_docs(category_name):
    """특정 카테고리의 모든 문서 가져오기"""
    print(f"\n{'='*70}")
    print(f"[Category] {category_name}")
    print(f"{'='*70}\n")
    
    docs = db.collection('hino_raw').where('category', '==', category_name).stream()
    
    results = []
    for doc in docs:
        data = doc.to_dict()
        results.append({
            'id': doc.id,
            'title': data.get('title', ''),
            'exercise_name': data.get('exercise_name', ''),
            'content': data.get('content', ''),
            'source_file': data.get('source_file', '')
        })
        print(f"OK {data.get('exercise_name', doc.id)}")
        print(f"   Title: {data.get('title', 'N/A')}")
        print()
    
    print(f"Total: {len(results)} docs\n")
    return results

if __name__ == '__main__':
    # 하이노이론부터 시작 (25개 문서)
    category = '하이노이론'
    docs = get_category_docs(category)
    
    # 내용 출력
    print("\n" + "="*70)
    print("📄 문서 내용:")
    print("="*70 + "\n")
    
    for i, doc in enumerate(docs, 1):
        print(f"\n### [{i}] {doc['exercise_name']} ###\n")
        # 내용 앞부분만 출력 (너무 길면 잘라냄)
        content = doc['content']
        if len(content) > 500:
            print(content[:500] + "\n... (생략)")
        else:
            print(content)
        print("\n" + "-"*70)
