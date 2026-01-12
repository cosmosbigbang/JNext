"""
카테고리별 공통이론 생성
6개 카테고리의 공통 원리/철학 정리
"""
import sys
import os
from dotenv import load_dotenv
import google.generativeai as genai
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

# .env 로드
load_dotenv()

sys.stdout.reconfigure(encoding='utf-8')

# Firebase 초기화
if not firebase_admin._apps:
    cred = credentials.Certificate('jnext-service-account.json')
    firebase_admin.initialize_app(cred)

db = firestore.client()

# Gemini API 설정
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY 환경 변수가 설정되지 않았습니다")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash-exp')


# 카테고리별 운동 매핑
CATEGORIES = {
    '하이노워밍': ['하이노워밍벤치'],
    '하이노골반': ['하이노골반상하', '하이노골반좌우', '하이노골반돌리기', '하이노골반벌리기'],
    '하이노워킹': ['하이노워킹전진', '하이노워킹주먹', '하이노워킹크로스', '하이노워킹퐁당퐁당'],
    '하이노스케이팅': ['하이노스케이팅좌우', '하이노스케이팅전진', '하이노스케이팅코너웍'],
    '하이노풋삽': ['하이노풋삽벽두손', '하이노풋삽벽한손'],
    '하이노철봉': ['하이노철봉한손']
}


def get_category_exercises(category):
    """카테고리의 모든 운동 정보 수집"""
    exercise_data = []
    
    # hino_raw에서 카테고리로 검색
    docs = db.collection('hino_raw').where(
        'category', '==', category
    ).stream()
    
    for doc in docs:
        data = doc.to_dict()
        name = data.get('exercise_name') or data.get('doc_id') or data.get('title', '')
        
        if name:  # 이름이 있으면 추가
            exercise_data.append({
                'name': name,
                'content': data.get('content', ''),
                'category': category
            })
    
    return exercise_data


def get_theory_context():
    """전체 이론 요약 가져오기"""
    # theory_summary.txt 읽기
    try:
        with open('theory_summary.txt', 'r', encoding='utf-8') as f:
            return f.read()
    except:
        # 없으면 Firestore에서
        docs = db.collection('hino_draft').where(
            'content_type', '==', 'theory_integrated'
        ).where(
            'length_level', '==', 'summary'
        ).limit(1).stream()
        
        for doc in docs:
            return doc.to_dict().get('content', '')
        
        return '하이노밸런스: 한 발 운동으로 뇌를 자극하는 혁신적 건강법'


def create_category_theory(category):
    """카테고리별 공통이론 생성"""
    print(f"\n{'='*70}")
    print(f"📚 {category} 공통이론 생성 중...")
    print(f"{'='*70}\n")
    
    # 1. 운동 정보 수집
    exercises = get_category_exercises(category)
    if not exercises:
        print(f"❌ {category}의 운동 정보를 찾을 수 없습니다.")
        return None
    
    print(f"✓ {len(exercises)}개 운동 수집:")
    for ex in exercises:
        print(f"  - {ex['name']}")
    
    # 2. 전체 이론 요약 가져오기
    theory_summary = get_theory_context()
    
    # 3. AI에게 공통이론 생성 요청
    print(f"\n🤖 AI 생성 중...\n")
    
    exercises_text = "\n\n".join([
        f"## {ex['name']}\n{ex['content'][:1000]}..."
        for ex in exercises
    ])
    
    prompt = f"""
당신은 하이노밸런스 이론 전문가입니다.

## 하이노밸런스 전체 이론 (요약)
{theory_summary}

## {category} 카테고리 운동들
{exercises_text}

## 요청사항
위 {len(exercises)}개 운동의 **공통 원리와 철학**을 정리해주세요.

**작성 가이드:**
1. 카테고리 개요 (이 카테고리가 하이노밸런스에서 어떤 역할?)
2. 핵심 원리 (이 운동들이 공유하는 과학적/의학적 원리)
3. 운동 철학 (왜 이런 방식으로 움직이는가?)
4. 기대 효과 (신체적, 정신적, 뇌과학적 효과)
5. 실천 가이드 (이 카테고리 운동을 할 때 핵심 포인트)

**목표 길이:** 1,500-2,500자
**톤:** 전문적이면서도 이해하기 쉽게
**포함 필수:** 가속도, 신경가소성, 불균형의 의미 등 하이노밸런스 핵심 개념

한글로 작성해주세요.
"""
    
    response = model.generate_content(prompt)
    theory_text = response.text
    
    # 4. Firestore에 저장
    theory_doc = {
        'content_type': 'category_theory',
        'category': category,
        'exercise_count': len(exercises),
        'exercise_names': [ex['name'] for ex in exercises],
        'content': theory_text,
        'created_at': datetime.now(),
        'status': 'draft'
    }
    
    doc_ref = db.collection('hino_draft').document()
    doc_ref.set(theory_doc)
    
    # 5. 파일로도 저장
    filename = f"category_theory_{category}.txt"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"# {category} 공통이론\n\n")
        f.write(f"생성일: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        f.write(f"운동 수: {len(exercises)}개\n\n")
        f.write("="*70 + "\n\n")
        f.write(theory_text)
    
    print(f"✅ 생성 완료!")
    print(f"   Firestore ID: {doc_ref.id}")
    print(f"   파일: {filename}")
    print(f"   길이: {len(theory_text):,}자\n")
    
    return doc_ref.id


def main():
    """모든 카테고리 공통이론 생성"""
    print("\n" + "🎓"*35)
    print("하이노밸런스 카테고리별 공통이론 생성")
    print("🎓"*35 + "\n")
    
    results = {}
    
    for category in CATEGORIES.keys():
        try:
            doc_id = create_category_theory(category)
            results[category] = doc_id
        except Exception as e:
            print(f"❌ {category} 생성 실패: {e}\n")
            results[category] = None
    
    # 최종 결과
    print("\n" + "="*70)
    print("📊 생성 결과 요약")
    print("="*70 + "\n")
    
    success_count = sum(1 for v in results.values() if v)
    
    for category, doc_id in results.items():
        status = "✅" if doc_id else "❌"
        print(f"{status} {category}: {doc_id or 'FAILED'}")
    
    print(f"\n총 {success_count}/{len(CATEGORIES)}개 성공\n")


if __name__ == '__main__':
    main()
