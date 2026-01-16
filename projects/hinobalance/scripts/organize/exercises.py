"""
개별 운동 상세 정리
15개 운동을 구조화된 형식으로 정리
"""
import sys
import os
from pathlib import Path
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
    cred = credentials.Certificate('../jnext-service-account.json')
    firebase_admin.initialize_app(cred)

db = firestore.client()

# Gemini API 설정
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY 환경 변수가 설정되지 않았습니다")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash-exp')


# 출시 운동 15개
EXERCISES = [
    '하이노워밍벤치',
    '하이노골반상하', '하이노골반좌우', '하이노골반돌리기', '하이노골반벌리기',
    '하이노워킹전진', '하이노워킹주먹', '하이노워킹크로스', '하이노워킹퐁당퐁당',
    '하이노스케이팅좌우', '하이노스케이팅전진', '하이노스케이팅코너웍',
    '하이노풋삽벽두손', '하이노풋삽벽한손',
    '하이노철봉한손'
]


def get_exercise_data(exercise_name):
    """운동 원본 데이터 가져오기"""
    docs = db.collection('hino_raw').where(
        'exercise_name', '==', exercise_name
    ).limit(1).stream()
    
    for doc in docs:
        return doc.to_dict()
    
    return None


def get_category_theory(category):
    """카테고리 공통이론 가져오기"""
    docs = db.collection('hino_draft').where(
        'content_type', '==', 'category_theory'
    ).where(
        'category', '==', category
    ).limit(1).stream()
    
    for doc in docs:
        return doc.to_dict().get('content', '')
    
    return ''


def organize_exercise(exercise_name):
    """개별 운동 상세 정리"""
    print(f"\n{'='*70}")
    print(f"🏋️ {exercise_name} 상세 정리 중...")
    print(f"{'='*70}\n")
    
    # 1. 원본 데이터 가져오기
    raw_data = get_exercise_data(exercise_name)
    if not raw_data:
        print(f"❌ {exercise_name} 데이터를 찾을 수 없습니다.")
        return None
    
    category = raw_data.get('category', '')
    content = raw_data.get('content', '')
    
    print(f"✓ 원본 데이터: {len(content):,}자")
    
    # 2. 카테고리 공통이론 가져오기
    category_theory = get_category_theory(category)
    print(f"✓ 카테고리 이론: {len(category_theory):,}자")
    
    # 3. AI에게 구조화 요청
    print(f"\n🤖 AI 구조화 중...\n")
    
    prompt = f"""
당신은 하이노밸런스 운동 전문가입니다.

## 카테고리 공통이론
{category_theory[:1000]}...

## 운동 원본 내용
{content}

## 운동명
{exercise_name}

## 요청사항
위 운동을 다음 구조로 상세하게 정리해주세요:

### 1. 운동 개요
- 한 줄 설명 (20자 이내)
- 난이도 (초급/중급/고급)
- 소요 시간 (분)
- 필요 도구

### 2. 핵심 원리
- 이 운동이 왜 효과적인가? (하이노밸런스 이론 기반)
- 어떤 신체 부위에 어떻게 작용하는가?
- 가속도/불균형/신경가소성 관점 설명

### 3. 동작 가이드
- 시작 자세
- 동작 순서 (1, 2, 3...)
- 호흡법
- 핵심 포인트

### 4. 주의사항
- 흔한 실수
- 피해야 할 자세
- 안전 수칙

### 5. 기대 효과
- 단기 효과 (1-2주)
- 중기 효과 (1-2개월)
- 장기 효과 (3개월 이상)
- 신체/정신/뇌과학적 효과

### 6. 응용 버전
- 더 쉬운 버전
- 더 어려운 버전
- 조합 추천

**목표 길이:** 2,000-3,000자
**톤:** 전문적이면서도 친근하게
**포함 필수:** 구체적인 동작, 과학적 근거, 실용적 팁

한글로 작성해주세요.
"""
    
    response = model.generate_content(prompt)
    organized_text = response.text
    
    # 4. Firestore에 저장
    exercise_doc = {
        'content_type': 'exercise_detailed',
        'exercise_name': exercise_name,
        'category': category,
        'original_content': content,
        'organized_content': organized_text,
        'created_at': datetime.now(),
        'status': 'draft'
    }
    
    doc_ref = db.collection('hino_draft').document()
    doc_ref.set(exercise_doc)
    
    # 5. 파일로도 저장
    filename = f"exercise_{exercise_name}.txt"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"# {exercise_name} 상세 가이드\n\n")
        f.write(f"생성일: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        f.write(f"카테고리: {category}\n\n")
        f.write("="*70 + "\n\n")
        f.write(organized_text)
    
    print(f"✅ 정리 완료!")
    print(f"   Firestore ID: {doc_ref.id}")
    print(f"   파일: {filename}")
    print(f"   길이: {len(organized_text):,}자\n")
    
    return doc_ref.id


def main():
    """모든 운동 상세 정리"""
    print("\n" + "🏋️"*35)
    print("하이노밸런스 개별 운동 상세 정리")
    print("🏋️"*35 + "\n")
    
    results = {}
    
    for i, exercise_name in enumerate(EXERCISES, 1):
        print(f"\n[{i}/{len(EXERCISES)}] 진행 중...\n")
        
        try:
            doc_id = organize_exercise(exercise_name)
            results[exercise_name] = doc_id
        except Exception as e:
            print(f"❌ {exercise_name} 정리 실패: {e}\n")
            results[exercise_name] = None
    
    # 최종 결과
    print("\n" + "="*70)
    print("📊 정리 결과 요약")
    print("="*70 + "\n")
    
    success_count = sum(1 for v in results.values() if v)
    
    for exercise_name, doc_id in results.items():
        status = "✅" if doc_id else "❌"
        print(f"{status} {exercise_name}")
    
    print(f"\n총 {success_count}/{len(EXERCISES)}개 성공\n")


if __name__ == '__main__':
    main()
