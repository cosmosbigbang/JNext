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
    "하이노 워밍 팔 돌리기: 효과" -> "하이노워밍팔돌리기: 효과"
    
    규칙:
    1. "하이노"로 시작하는 단어는 다음 특수문자(:, ,, . 등) 나올 때까지 모든 띄어쓰기 제거
    2. 특수문자 이후는 그대로 유지
    """
    if not title or '하이노' not in title:
        return title
    
    # "하이노"로 시작하는 부분 찾기
    result = []
    parts = re.split(r'([:\.,!\?])', title)  # 특수문자 기준으로 분리 (구분자 포함)
    
    for i, part in enumerate(parts):
        if '하이노' in part:
            # 하이노가 포함된 부분은 모든 띄어쓰기 제거
            result.append(part.replace(' ', ''))
        else:
            result.append(part)
    
    return ''.join(result)


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
