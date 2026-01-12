"""
웹/앱 확인용 상태 점검
hino_draft의 모든 데이터를 카테고리별로 정리
"""
import sys
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

# Firebase 초기화
if not firebase_admin._apps:
    cred = credentials.Certificate('jnext-service-account.json')
    firebase_admin.initialize_app(cred)

db = firestore.client()


def check_draft_status():
    """hino_draft 전체 상태 점검"""
    print("\n" + "="*70)
    print("📦 hino_draft 상세 현황 (웹/앱 확인용)")
    print("="*70 + "\n")
    
    docs = db.collection('hino_draft').stream()
    
    categories = {
        'theory_integrated': [],      # 통합 이론
        'category_theory': [],         # 카테고리 공통이론
        'exercise_detailed': [],       # 개별 운동 상세
        'meme_scenario': [],           # 밈 시나리오
        'sitcom_episode': [],          # 시트콤 에피소드
        'sitcom_scene': [],            # 시트콤 장면
        'meme': [],                    # 밈
        'short': [],                   # 숏폼
    }
    
    for doc in docs:
        data = doc.to_dict()
        content_type = data.get('content_type', 'unknown')
        
        if content_type in categories:
            categories[content_type].append({
                'id': doc.id,
                'data': data
            })
        else:
            if 'unknown' not in categories:
                categories['unknown'] = []
            categories['unknown'].append({
                'id': doc.id,
                'data': data
            })
    
    # 결과 출력
    total = 0
    
    # 1. 통합 이론
    if categories['theory_integrated']:
        print("📚 통합 이론 (3개)")
        print("-" * 70)
        for item in categories['theory_integrated']:
            data = item['data']
            level = data.get('length_level', 'N/A')
            length = len(data.get('content', ''))
            print(f"  • {level:10s} - {length:6,}자 - ID: {item['id'][:10]}...")
        print()
        total += len(categories['theory_integrated'])
    
    # 2. 카테고리 공통이론
    if categories['category_theory']:
        print("🏷️  카테고리 공통이론 (6개)")
        print("-" * 70)
        for item in categories['category_theory']:
            data = item['data']
            category = data.get('category', 'N/A')
            length = len(data.get('content', ''))
            ex_count = data.get('exercise_count', 0)
            print(f"  • {category:15s} - {ex_count}개 운동 - {length:5,}자 - ID: {item['id'][:10]}...")
        print()
        total += len(categories['category_theory'])
    
    # 3. 개별 운동 상세
    if categories['exercise_detailed']:
        print("🏋️  개별 운동 상세 (15개)")
        print("-" * 70)
        
        # 카테고리별로 그룹화
        by_cat = {}
        for item in categories['exercise_detailed']:
            data = item['data']
            cat = data.get('category', '기타')
            if cat not in by_cat:
                by_cat[cat] = []
            by_cat[cat].append(item)
        
        for cat, items in sorted(by_cat.items()):
            print(f"\n  [{cat}] {len(items)}개")
            for item in items:
                data = item['data']
                ex_name = data.get('exercise_name', 'N/A')
                length = len(data.get('organized_content', ''))
                print(f"    - {ex_name:20s} {length:5,}자 - ID: {item['id'][:10]}...")
        print()
        total += len(categories['exercise_detailed'])
    
    # 4. 밈 시나리오 (기존)
    if categories['meme_scenario']:
        print("💡 밈 시나리오 (7개)")
        print("-" * 70)
        for item in categories['meme_scenario']:
            data = item['data']
            doc_id = data.get('doc_id', 'N/A')
            length = len(data.get('content', ''))
            print(f"  • {doc_id:30s} - {length:5,}자 - ID: {item['id'][:10]}...")
        print()
        total += len(categories['meme_scenario'])
    
    # 5. 시트콤 에피소드
    if categories['sitcom_episode']:
        print("🎬 시트콤 에피소드")
        print("-" * 70)
        for item in categories['sitcom_episode']:
            data = item['data']
            title = data.get('title', 'N/A')
            scene_count = data.get('scene_count', 0)
            print(f"  • {title:30s} - {scene_count}개 장면 - ID: {item['id'][:10]}...")
        print()
        total += len(categories['sitcom_episode'])
    
    # 6. 시트콤 장면
    if categories['sitcom_scene']:
        print("🎬 시트콤 장면")
        print("-" * 70)
        
        # 에피소드별로 그룹화
        by_episode = {}
        for item in categories['sitcom_scene']:
            data = item['data']
            ep_title = data.get('episode_title', '개별 장면')
            if ep_title not in by_episode:
                by_episode[ep_title] = []
            by_episode[ep_title].append(item)
        
        for ep_title, items in sorted(by_episode.items()):
            print(f"\n  [{ep_title}] {len(items)}개 장면")
            for item in items:
                data = item['data']
                scene_num = data.get('scene_number', '?')
                scene_title = data.get('title', 'N/A')
                print(f"    - Scene {scene_num}: {scene_title:30s} - ID: {item['id'][:10]}...")
        print()
        total += len(categories['sitcom_scene'])
    
    # 7. 밈 (신규)
    if categories['meme']:
        print("💡 밈 (신규)")
        print("-" * 70)
        for item in categories['meme']:
            data = item['data']
            theme = data.get('theme', 'N/A')
            style = data.get('style', 'N/A')
            print(f"  • {theme:40s} ({style:8s}) - ID: {item['id'][:10]}...")
        print()
        total += len(categories['meme'])
    
    # 8. 숏폼
    if categories['short']:
        print("🎥 숏폼")
        print("-" * 70)
        for item in categories['short']:
            data = item['data']
            ex_name = data.get('exercise_name', 'N/A')
            angle = data.get('angle', 'N/A')
            print(f"  • {ex_name:25s} ({angle:10s}) - ID: {item['id'][:10]}...")
        print()
        total += len(categories['short'])
    
    # 9. 기타/알 수 없음
    if categories.get('unknown'):
        print("❓ 기타")
        print("-" * 70)
        for item in categories['unknown']:
            data = item['data']
            print(f"  • ID: {item['id']} - {list(data.keys())[:3]}")
        print()
        total += len(categories['unknown'])
    
    # 요약
    print("="*70)
    print(f"📊 총 {total}개 문서")
    print("="*70)
    print()
    
    return categories


def check_content_status():
    """hino_content 컬렉션 확인"""
    print("\n" + "="*70)
    print("🎨 hino_content 상세 현황")
    print("="*70 + "\n")
    
    docs = db.collection('hino_content').stream()
    
    count = 0
    by_type = {}
    
    for doc in docs:
        data = doc.to_dict()
        content_type = data.get('content_type', 'unknown')
        
        if content_type not in by_type:
            by_type[content_type] = []
        
        by_type[content_type].append({
            'id': doc.id,
            'data': data
        })
        count += 1
    
    if count == 0:
        print("📭 비어있음\n")
        return
    
    for content_type, items in sorted(by_type.items()):
        print(f"{content_type}: {len(items)}개")
        for item in items[:3]:  # 처음 3개만
            print(f"  - ID: {item['id'][:15]}...")
        if len(items) > 3:
            print(f"  ... 외 {len(items)-3}개 더")
        print()
    
    print(f"총 {count}개 문서\n")


def main():
    print("\n" + "🔍"*35)
    print("하이노밸런스 웹/앱 확인용 상태 점검")
    print("🔍"*35)
    
    draft = check_draft_status()
    check_content_status()
    
    print("\n" + "="*70)
    print("💡 확인 가이드")
    print("="*70)
    print("""
1. 웹/앱에서 hino_draft 컬렉션 조회
2. 각 카테고리별로 내용 확인:
   - 통합 이론 (요약/중간/전체)
   - 카테고리 공통이론 (6개)
   - 개별 운동 상세 (15개)
   - 밈/시트콤/숏폼 콘텐츠

3. 확인할 항목:
   ✓ 내용 정확성
   ✓ 오타/누락
   ✓ 형식/구조
   ✓ 길이 적정성

4. 수정 필요 시 → 수정 후 재확인
5. 확정 시 → hino_final로 이동 (다음 단계)
    """)
    print("="*70 + "\n")


if __name__ == '__main__':
    main()
