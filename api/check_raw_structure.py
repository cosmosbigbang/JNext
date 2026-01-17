"""
hino_raw 컬렉션 구조 확인
"""
import firebase_admin
from firebase_admin import credentials, firestore
from collections import defaultdict

# Firebase 초기화
if not firebase_admin._apps:
    cred = credentials.Certificate('jnext-service-account.json')
    firebase_admin.initialize_app(cred)

db = firestore.client()

def check_raw_structure():
    """raw 컬렉션 구조 분석"""
    docs = db.collection('hino_raw').stream()
    
    category_groups = defaultdict(list)
    
    for doc in docs:
        data = doc.to_dict()
        category = data.get('category') or data.get('카테고리') or 'Unknown'
        exercise_name = data.get('exercise_name') or doc.id
        
        category_groups[category].append({
            'id': doc.id,
            'exercise_name': exercise_name,
            'title': data.get('title') or '',
        })
    
    print(f"{'='*70}")
    print(f"📊 hino_raw 구조 분석")
    print(f"{'='*70}\n")
    
    for category, items in sorted(category_groups.items()):
        print(f"\n【{category}】 ({len(items)}개)")
        for item in items:
            print(f"  - {item['id']}: {item['title'][:50]}")
    
    return category_groups

if __name__ == '__main__':
    check_raw_structure()
