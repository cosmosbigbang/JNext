"""
하이노밸런스 DB 현황 점검
"""
import sys
import firebase_admin
from firebase_admin import credentials, firestore
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')

if not firebase_admin._apps:
    cred = credentials.Certificate('jnext-service-account.json')
    firebase_admin.initialize_app(cred)

db = firestore.client()

def check_collection_status(collection_name):
    """컬렉션 상태 확인"""
    print(f"\n{'='*70}")
    print(f"📦 {collection_name} 컬렉션 현황")
    print(f"{'='*70}\n")
    
    docs = db.collection(collection_name).stream()
    
    by_category = defaultdict(list)
    by_content_type = defaultdict(list)
    total = 0
    
    for doc in docs:
        data = doc.to_dict()
        category = data.get('category', 'N/A')
        content_type = data.get('content_type', 'N/A')
        exercise_name = data.get('exercise_name', doc.id)
        
        by_category[category].append(exercise_name)
        by_content_type[content_type].append(exercise_name)
        total += 1
    
    print(f"총 문서: {total}개\n")
    
    print("📂 카테고리별:")
    for cat, names in sorted(by_category.items()):
        print(f"   {cat}: {len(names)}개")
        if len(names) <= 10:
            for name in sorted(names):
                print(f"      - {name}")
    
    if by_content_type and 'N/A' not in by_content_type or len(by_content_type) > 1:
        print(f"\n📝 콘텐츠 타입별:")
        for ctype, names in sorted(by_content_type.items()):
            print(f"   {ctype}: {len(names)}개")
    
    return total, by_category, by_content_type

def check_missing_exercises():
    """출시 18개 운동 중 누락 확인"""
    print(f"\n{'='*70}")
    print(f"🔍 출시 운동 18개 매칭 상태")
    print(f"{'='*70}\n")
    
    RELEASE_EXERCISES = [
        # 워밍 (2개)
        '하이노워밍벤치', '하이노워밍기본',
        # 골반 (4개)
        '하이노골반상하', '하이노골반좌우', '하이노골반돌리기', '하이노골반벌리기',
        # 워킹 (4개)
        '하이노워킹전진', '하이노워킹주먹', '하이노워킹크로스', '하이노워킹퐁당퐁당',
        # 스케이팅 (4개)
        '하이노스케이팅좌우', '하이노스케이팅전진', '하이노스케이팅코너웍', '하이노스케이팅후진',
        # 풋삽 (2개)
        '하이노풋삽벽두손', '하이노풋삽벽한손',
        # 철봉 (2개)
        '하이노철봉한손', '하이노철봉두손'
    ]
    
    # hino_raw에서 확인
    raw_docs = db.collection('hino_raw').stream()
    raw_exercises = set()
    for doc in raw_docs:
        data = doc.to_dict()
        exercise_name = data.get('exercise_name', '')
        if exercise_name and '하이노' in exercise_name:
            raw_exercises.add(exercise_name)
    
    found = []
    missing = []
    
    for ex in RELEASE_EXERCISES:
        if ex in raw_exercises:
            found.append(ex)
        else:
            missing.append(ex)
    
    print(f"✅ 매칭 완료: {len(found)}개")
    for ex in found:
        print(f"   - {ex}")
    
    print(f"\n❌ 누락/수동 정리 필요: {len(missing)}개")
    for ex in missing:
        print(f"   - {ex}")
    
    return found, missing

if __name__ == '__main__':
    print("\n" + "="*70)
    print("하이노밸런스 DB 전체 현황 점검")
    print("="*70)
    
    # 1. hino_raw 확인
    raw_total, raw_by_cat, _ = check_collection_status('hino_raw')
    
    # 2. hino_draft 확인
    try:
        draft_total, draft_by_cat, draft_by_type = check_collection_status('hino_draft')
    except Exception as e:
        print(f"\n⚠️  hino_draft 없음 (생성 필요)")
        draft_total = 0
    
    # 3. 출시 운동 매칭 확인
    found, missing = check_missing_exercises()
    
    # 4. 요약
    print(f"\n{'='*70}")
    print(f"📊 전체 요약")
    print(f"{'='*70}")
    print(f"hino_raw: {raw_total}개")
    if draft_total > 0:
        print(f"hino_draft: {draft_total}개")
    print(f"\n출시 운동 18개:")
    print(f"  ✅ 완료: {len(found)}개")
    print(f"  ❌ 누락: {len(missing)}개")
    
    print(f"\n{'='*70}")
    print(f"🎯 다음 작업 제안")
    print(f"{'='*70}")
    
    suggestions = []
    
    if missing:
        suggestions.append(f"1. 누락된 {len(missing)}개 운동 노션 파일 찾기 또는 새로 작성")
    
    if draft_total == 0:
        suggestions.append("2. hino_draft 컬렉션 세팅 (이론 통합 버전 저장)")
    
    if raw_by_cat.get('하이노이론', []):
        suggestions.append("3. AI에게 하이노전체이론 요약/중간 버전 생성 요청")
    
    suggestions.append("4. 카테고리별 공통이론 정리 (워밍→골반→워킹→스케이팅→풋삽→철봉)")
    suggestions.append("5. 개별 운동 상세 정리 (15개)")
    
    for s in suggestions:
        print(f"   {s}")
