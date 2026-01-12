"""
하이노이론 24개 문서 분류 및 처리
- 통합 대상: 이론/원리/평가/가치 → 요약/중간/최대 생성
- 개별 보존: 밈/시나리오/설계서 → 원본 유지
"""
import sys
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

if not firebase_admin._apps:
    cred = credentials.Certificate('jnext-service-account.json')
    firebase_admin.initialize_app(cred)

db = firestore.client()

# 24개 문서 분류
THEORY_DOCS = {
    # === 통합 대상 (이론/원리/평가/가치) ===
    'integrate': [
        '가치_워킹소감',
        '가치_학문적운동학적',
        '원리_01',
        '원리_02',
        '원리_3대원리',
        '이론_16개요점백업',
        '이론_251228',
        '이론_가속도물리',
        '이론_개선260111',
        '이론_계단의의미',
        '이론_딥싱크분석',
        '이론_불균형의미',
        '이론_최종241228',
        '평가_젠3대원리',
        '평가_종합',
        '평가_지큐',
        '평가_하이노밸런스'
    ],
    
    # === 개별 보존 (밈/시나리오/설계) ===
    'preserve': [
        '밈_251218',        # 시트콤 시나리오
        '밈_DB구조',        # DB 설계서
        '밈_fk',            # DB 구조 논의
        '밈_가치평가',      # 개별 운동 평가 템플릿
        '밈_스케이팅',      # 스케이팅 시나리오
        '밈_탄생서사',      # J와 지피 스토리
        '밈_프리으싸'       # 운동 카드 템플릿
    ]
}

def get_all_theory_docs():
    """하이노이론 24개 모두 가져오기"""
    print("\n" + "="*70)
    print("하이노이론 문서 수집 중...")
    print("="*70 + "\n")
    
    docs = db.collection('hino_raw').where('category', '==', '하이노이론').stream()
    
    all_docs = {}
    for doc in docs:
        data = doc.to_dict()
        exercise_name = data.get('exercise_name', '')
        all_docs[exercise_name] = {
            'id': doc.id,
            'exercise_name': exercise_name,
            'content': data.get('content', ''),
            'title': data.get('title', '')
        }
    
    print(f"총 {len(all_docs)}개 문서 수집 완료!\n")
    return all_docs

def classify_docs(all_docs):
    """통합/보존 분류"""
    integrate_docs = []
    preserve_docs = []
    
    for name in THEORY_DOCS['integrate']:
        if name in all_docs:
            integrate_docs.append(all_docs[name])
    
    for name in THEORY_DOCS['preserve']:
        if name in all_docs:
            preserve_docs.append(all_docs[name])
    
    return integrate_docs, preserve_docs

def save_to_draft(docs, content_type):
    """hino_draft 컬렉션에 저장 (개별)"""
    print(f"\n📝 {content_type} 문서 저장 중...")
    
    for doc in docs:
        draft_data = {
            'exercise_name': doc['exercise_name'],
            'title': doc['title'],
            'content': doc['content'],
            'category': '하이노이론',
            'content_type': content_type,  # 'theory_integrated' 또는 'meme_scenario'
            'source': 'notion',
            'created_at': datetime.now(),
            'updated_at': datetime.now(),
            'status': 'draft'
        }
        
        # exercise_name으로 문서 ID 생성
        doc_id = doc['exercise_name']
        db.collection('hino_draft').document(doc_id).set(draft_data)
        print(f"  ✓ {doc['exercise_name']}")

def create_integrated_theory(integrate_docs):
    """통합 이론 3단계 생성"""
    print("\n" + "="*70)
    print("통합 이론 생성 중...")
    print("="*70 + "\n")
    
    # 전체 내용 하나로 합치기
    full_content = ""
    for i, doc in enumerate(integrate_docs, 1):
        full_content += f"\n\n### [{i}] {doc['exercise_name']} ###\n\n"
        full_content += doc['content']
        full_content += "\n\n" + "-"*70
    
    # 3단계 버전 생성 (실제로는 AI에게 요청해야 하지만 일단 구조만)
    versions = {
        'summary': {
            'exercise_name': '하이노전체이론_요약',
            'title': '하이노밸런스 핵심 이론 (요약)',
            'content': f"[요약 버전 - 약 2000자]\n\n{full_content[:2000]}...",
            'length_level': 'summary',
            'target_length': 2000
        },
        'medium': {
            'exercise_name': '하이노전체이론_중간',
            'title': '하이노밸런스 전체 이론 (중간)',
            'content': f"[중간 버전 - 약 10000자]\n\n{full_content[:10000]}...",
            'length_level': 'medium',
            'target_length': 10000
        },
        'full': {
            'exercise_name': '하이노전체이론_전체',
            'title': '하이노밸런스 전체 이론 (완전판)',
            'content': full_content,
            'length_level': 'full',
            'target_length': len(full_content)
        }
    }
    
    # 파일로도 저장
    with open('theory_integrated_full.txt', 'w', encoding='utf-8') as f:
        f.write(full_content)
    
    print(f"✅ 통합 이론 전체: {len(full_content):,} 자")
    print(f"   - 요약: ~2,000자")
    print(f"   - 중간: ~10,000자")
    print(f"   - 전체: {len(full_content):,}자")
    
    return versions

if __name__ == '__main__':
    print("\n" + "="*70)
    print("하이노이론 분류 및 정리 시작")
    print("="*70)
    
    # 1. 전체 문서 수집
    all_docs = get_all_theory_docs()
    
    # 2. 통합/보존 분류
    integrate_docs, preserve_docs = classify_docs(all_docs)
    
    print("="*70)
    print(f"📊 분류 결과:")
    print(f"   통합 대상 (이론/원리/평가): {len(integrate_docs)}개")
    print(f"   개별 보존 (밈/시나리오): {len(preserve_docs)}개")
    print("="*70 + "\n")
    
    # 3. 개별 보존 문서 → hino_draft 저장
    if preserve_docs:
        save_to_draft(preserve_docs, 'meme_scenario')
    
    # 4. 통합 이론 생성
    if integrate_docs:
        versions = create_integrated_theory(integrate_docs)
        
        # 통합 이론 3버전도 draft에 저장
        for ver_name, ver_data in versions.items():
            draft_data = {
                'exercise_name': ver_data['exercise_name'],
                'title': ver_data['title'],
                'content': ver_data['content'],
                'category': '하이노이론',
                'content_type': 'theory_integrated',
                'length_level': ver_data['length_level'],
                'target_length': ver_data['target_length'],
                'source': 'integrated',
                'created_at': datetime.now(),
                'updated_at': datetime.now(),
                'status': 'draft'
            }
            
            db.collection('hino_draft').document(ver_data['exercise_name']).set(draft_data)
            print(f"  ✓ {ver_data['exercise_name']} 저장")
    
    print("\n" + "="*70)
    print("✅ 작업 완료!")
    print("="*70)
    print(f"\n다음 단계:")
    print(f"1. theory_integrated_full.txt 파일 확인")
    print(f"2. AI에게 요약/중간 버전 생성 요청")
    print(f"3. hino_draft에서 검토 후 hino_final로 이동")
