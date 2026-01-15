"""
하이노밸런스 제목 일괄 수정 스크립트
띄어쓰기된 제목을 하이노밸런스 작명법(붙여쓰기)으로 변경
"""
import os
import sys
import django
import re

# Django 설정
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from firebase_admin import firestore

def normalize_hino_title(title):
    """
    하이노밸런스 제목 정규화
    "하이노 풋삽 벽 두손 운동 분석" -> "하이노풋삽벽두손 운동 분석"
    
    규칙:
    1. "하이노" 단어 + 뒤따르는 한글 단어 3개까지만 붙여쓰기
    2. 그 이후 단어는 띄어쓰기 유지 ("운동 분석", "효과", "방법" 등)
    """
    if not title or '하이노' not in title:
        return title
    
    words = title.split()
    result = []
    i = 0
    
    while i < len(words):
        if '하이노' in words[i]:
            # 하이노 단어 다음 한글 단어들만 붙이기 (최대 3개)
            combined = words[i]
            i += 1
            count = 0
            while i < len(words) and count < 3 and re.match(r'^[가-힣]+$', words[i]):
                # 특수문자 포함 단어면 중단
                if ':' in words[i] or ',' in words[i] or '.' in words[i]:
                    break
                combined += words[i]
                i += 1
                count += 1
            result.append(combined)
        else:
            result.append(words[i])
            i += 1
    
    return ' '.join(result)


def fix_titles():
    """모든 컬렉션의 제목 일괄 수정"""
    db = firestore.client()
    
    collections = ['raw', 'draft', 'final']
    project_id = 'hinobalance'
    
    total_fixed = 0
    
    for collection in collections:
        print(f"\n=== {collection.upper()} 컬렉션 처리 중 ===")
        
        docs_ref = db.collection('projects').document(project_id).collection(collection)
        docs = docs_ref.stream()
        
        fixed_count = 0
        
        for doc in docs:
            data = doc.to_dict()
            old_title = data.get('제목') or data.get('title')
            
            if not old_title:
                continue
            
            new_title = normalize_hino_title(old_title)
            
            if new_title != old_title:
                print(f"  수정: '{old_title}' → '{new_title}'")
                
                # 제목 업데이트
                update_data = {}
                if '제목' in data:
                    update_data['제목'] = new_title
                if 'title' in data:
                    update_data['title'] = new_title
                
                doc.reference.update(update_data)
                fixed_count += 1
        
        print(f"{collection}: {fixed_count}개 수정 완료")
        total_fixed += fixed_count
    
    print(f"\n✅ 전체: {total_fixed}개 제목 수정 완료")


if __name__ == '__main__':
    print("하이노밸런스 제목 일괄 수정 시작...")
    print("예: '하이노 워밍 팔돌리기' → '하이노워밍팔돌리기'")
    
    response = input("\n계속하시겠습니까? (y/n): ")
    
    if response.lower() == 'y':
        fix_titles()
    else:
        print("취소됨")
