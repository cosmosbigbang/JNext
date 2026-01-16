"""
Firestore 마이그레이션: Flat → Hierarchical (상하위 구조)

기존: hino_raw, hino_draft, hino_final, hino_theory (루트 컬렉션)
신규: projects/{project_id}/{subcollection}

예:
  projects/
    └─ hinobalance/
        ├─ raw/
        ├─ draft/
        ├─ final/
        └─ theory/
"""
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime, timezone, timedelta
import time

# Firebase 초기화
if not firebase_admin._apps:
    cred = credentials.Certificate('../jnext-service-account.json')
    firebase_admin.initialize_app(cred)

db = firestore.client()
KST = timezone(timedelta(hours=9))

def migrate_to_hierarchical():
    """
    Flat 구조를 Hierarchical 구조로 마이그레이션
    """
    print("=" * 80)
    print("🔄 Firestore 마이그레이션 시작")
    print("=" * 80)
    print()
    
    # 1. 프로젝트 메타 정보 생성
    print("📝 Step 1: 프로젝트 메타 정보 생성")
    project_meta = {
        'display_name': '하이노밸런스',
        'description': '균형, 가속도, 불균형의 3대 원리 기반 운동 이론',
        'created_at': datetime.now(KST),
        'creator': 'J님',
        'collections': ['raw', 'draft', 'final', 'theory'],
        'status': 'active'
    }
    
    db.collection('projects').document('hinobalance').set(project_meta)
    print("✅ projects/hinobalance 문서 생성 완료")
    print()
    
    # 2. 마이그레이션 작업
    migrations = [
        ('hino_raw', 'raw'),
        ('hino_draft', 'draft'),
        ('hino_final', 'final'),
        ('hino_theory', 'theory')
    ]
    
    total_migrated = 0
    
    for old_collection, new_subcollection in migrations:
        print(f"🔄 Step 2: {old_collection} → projects/hinobalance/{new_subcollection}")
        print("-" * 80)
        
        # 기존 컬렉션 문서 조회
        docs = db.collection(old_collection).stream()
        
        count = 0
        batch = db.batch()
        batch_count = 0
        
        for doc in docs:
            # 새 경로에 복사
            new_ref = db.collection('projects').document('hinobalance').collection(new_subcollection).document(doc.id)
            batch.set(new_ref, doc.to_dict())
            
            count += 1
            batch_count += 1
            
            # Firestore 배치 제한: 500개
            if batch_count >= 500:
                batch.commit()
                print(f"  📦 배치 커밋: {count}개")
                batch = db.batch()
                batch_count = 0
                time.sleep(0.1)  # Rate limit 방지
        
        # 남은 배치 커밋
        if batch_count > 0:
            batch.commit()
        
        print(f"✅ {old_collection}: {count}개 문서 마이그레이션 완료")
        print()
        total_migrated += count
    
    print("=" * 80)
    print(f"🎉 마이그레이션 완료! 총 {total_migrated}개 문서 이동")
    print("=" * 80)
    print()
    
    # 3. 검증
    print("🔍 Step 3: 마이그레이션 검증")
    print("-" * 80)
    
    for _, subcollection in migrations:
        new_count = len(list(db.collection('projects').document('hinobalance').collection(subcollection).stream()))
        print(f"  projects/hinobalance/{subcollection}: {new_count}개 문서")
    
    print()
    print("⚠️  주의: 기존 컬렉션(hino_*)은 아직 삭제되지 않았습니다.")
    print("   검증 후 delete_old_collections.py로 삭제하세요.")
    print()


def delete_old_collections():
    """
    기존 flat 컬렉션 삭제 (백업 후 실행)
    """
    print("=" * 80)
    print("🗑️  기존 컬렉션 삭제 시작")
    print("=" * 80)
    print()
    
    confirm = input("⚠️  정말 삭제하시겠습니까? (yes 입력): ")
    if confirm != 'yes':
        print("❌ 취소됨")
        return
    
    old_collections = ['hino_raw', 'hino_draft', 'hino_final', 'hino_theory']
    
    for collection_name in old_collections:
        print(f"🗑️  {collection_name} 삭제 중...")
        
        docs = db.collection(collection_name).stream()
        batch = db.batch()
        batch_count = 0
        count = 0
        
        for doc in docs:
            batch.delete(doc.reference)
            count += 1
            batch_count += 1
            
            if batch_count >= 500:
                batch.commit()
                print(f"  삭제: {count}개")
                batch = db.batch()
                batch_count = 0
                time.sleep(0.1)
        
        if batch_count > 0:
            batch.commit()
        
        print(f"✅ {collection_name}: {count}개 문서 삭제 완료")
    
    print()
    print("🎉 모든 기존 컬렉션 삭제 완료!")


if __name__ == '__main__':
    print()
    print("📋 선택:")
    print("  1. 마이그레이션 (hino_* → projects/hinobalance/*)")
    print("  2. 기존 컬렉션 삭제 (백업 후)")
    print()
    
    choice = input("선택 (1 or 2): ").strip()
    
    if choice == '1':
        migrate_to_hierarchical()
    elif choice == '2':
        delete_old_collections()
    else:
        print("❌ 잘못된 선택")
