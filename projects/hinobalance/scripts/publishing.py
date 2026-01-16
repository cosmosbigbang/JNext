"""
Draft → Final 출판용 변환 자동화
JNext 통합 준비
"""
import firebase_admin
from firebase_admin import credentials, firestore
from pathlib import Path
import google.generativeai as genai
import os
from dotenv import load_dotenv
import time

# 환경 변수 로드
load_dotenv()

# Firebase 초기화
if not firebase_admin._apps:
    base_dir = Path(__file__).resolve().parent.parent.parent  # projects/hinobalance/scripts -> JNext root
    cred_path = base_dir / 'jnext-service-account.json'
    cred = credentials.Certificate(str(cred_path))
    firebase_admin.initialize_app(cred)

db = firestore.client()

# Gemini API 설정
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-2.0-flash-exp')

# 출판용 변환 시스템 프롬프트 (JNext용)
FINAL_PUBLISHING_PROMPT = """
# 하이노밸런스 이론 - 출판 완성 가이드

당신은 하이노밸런스 운동 철학을 출판물로 정제하는 전문가입니다.

## 현재 문제

draft 문서가 기계적입니다:
- "~이다. ~한다. ~된다." 단조로운 반복
- 짧은 문장만 나열 (리듬감 없음)
- 불릿 포인트 과다 (PPT처럼 보임)
- 철학적 깊이 부족

## 목표

**출판물 수준의 완성도**
- 자연스러운 문장 흐름
- 철학적 깊이와 전문성
- 읽는 순간 신뢰가 생기는 글

## 변환 원칙

### 1. 문장 구조
❌ 단조로운 나열:
```
하이노스케이팅은 핵심이다.
스케이팅을 모방한다.
움직임을 극대화한다.
```

✅ 자연스러운 흐름:
```
하이노스케이팅은 하이노밸런스의 핵심이다. 빙판 위 스케이팅 동작을 모방하여, 
일상 공간에서 3차원 움직임을 극대화하고 가속도 제어 능력을 끌어올린다.
```

### 2. 리듬과 호흡
- 짧은 문장 (5-15자)
- 중간 문장 (20-40자)
- 긴 문장 (50-80자)
→ **적절히 섞어서 리듬 만들기**

### 3. 강조 방법
❌ 불릿 포인트 남발
✅ 문장 자체로 강조
✅ 단락 분리
✅ 철학적 선언

### 4. 종결어미 다양화
❌ "~이다" 반복
✅ 다양한 표현:
- ~이다 / ~한다 / ~된다
- ~를 의미한다 / ~로 귀결된다
- ~에서 시작된다 / ~를 추구한다

### 5. 불릿 처리
❌ 
```
*   가속도
*   신경가소성
*   고유수용성
```

✅ 
```
세 기둥 위에 서 있다: 가속도, 신경가소성, 고유수용성 감각.
이 세 원리가 통합적으로 작동하며 신체의 잠재력을 끌어낸다.
```

## 양호한 예시 (참고용)

다음은 이미 출판 수준으로 정리된 문서입니다:

```
## 하이노철봉한손 운동 카테고리 분석

불균형 속에서 균형을 찾는다.
인체의 잠재력을 깨운다.
뇌 기능을 활성화한다.

'균형은 정지, 불균형은 움직임'
하이노밸런스의 핵심이다.

### 1. 카테고리 개요

불완전함에서 완전한 움직임이 시작된다.
한 손으로 철봉을 잡는다.
극심한 불균형이 시작된다.

뇌와 신경계는 적응하고 재조직된다.
안정성을 깨뜨려 성장을 만든다.
의도적 불균형은 진화의 촉매제다.
```

## 작업 지침

1. **원본 내용 보존**: 핵심 정보 유지
2. **자연스러운 재구성**: 기계적 나열 제거
3. **리듬감 부여**: 문장 길이 변화
4. **철학적 깊이**: 단순 설명 → 원리 제시
5. **불릿 최소화**: 문장으로 통합

## 결과물

변환된 텍스트만 출력하시오.
설명이나 주석 불필요.
"""

def refine_to_final(doc_id: str, content: str, category: str) -> dict:
    """Draft → Final 변환"""
    
    prompt = f"{FINAL_PUBLISHING_PROMPT}\n\n## 변환할 원본\n\n{content}"
    
    try:
        response = model.generate_content(
            prompt,
            generation_config={
                'temperature': 0.5,  # 창의성과 정확성 균형
                'top_p': 0.9,
                'top_k': 40,
                'max_output_tokens': 8192,
            }
        )
        
        refined = response.text.strip()
        
        return {
            'success': True,
            'refined_content': refined,
            'original_length': len(content),
            'refined_length': len(refined)
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def process_problem_docs():
    """문제 있는 category_theory 문서만 처리"""
    
    print("=" * 80)
    print("Draft → Final 출판용 변환 (JNext 프로토타입)")
    print("=" * 80)
    
    # 문제 있는 문서 ID들
    problem_docs = [
        'YQIoZQPkbhpYZ7Z2bXl7',  # 하이노워밍 (45점)
        '0k8dnxIYKoLavcO371lv',  # 하이노골반 (60점)
        'uaJkjx9lFjchpcWrS0hN',  # 하이노워킹 (60점)
        '1si9xZIPR0LJX1xXF4Wn',  # 하이노스케이팅 (50점)
        'NzeURHFvXOxAuQZRSVgI',  # 하이노풋삽 (불릿 21개)
        'HKKJBZkwnyn6z8878Uhr',  # 하이노철봉 (80점, 굵게 17회)
    ]
    
    draft_ref = db.collection('hino_draft')
    
    processed = 0
    errors = 0
    
    for doc_id in problem_docs:
        doc = draft_ref.document(doc_id).get()
        
        if not doc.exists:
            print(f"\n⚠️  문서 없음: {doc_id}")
            continue
        
        data = doc.to_dict()
        
        if 'content' not in data:
            print(f"\n⚠️  content 없음: {doc_id}")
            continue
        
        content = data['content']
        category = data.get('category', 'unknown')
        
        print(f"\n{'=' * 80}")
        print(f"📄 {doc_id}")
        print(f"   카테고리: {category}")
        print(f"   원본 길이: {len(content):,}자")
        print(f"{'=' * 80}")
        
        print(f"   🔄 젠에게 변환 요청...")
        result = refine_to_final(doc_id, content, category)
        
        if result['success']:
            refined = result['refined_content']
            
            print(f"   📊 결과:")
            print(f"      원본: {result['original_length']:,}자")
            print(f"      변환: {result['refined_length']:,}자")
            
            # Firestore 업데이트
            try:
                doc.reference.update({
                    'content': refined,
                    'updated_at': firestore.SERVER_TIMESTAMP,
                    'final_refined': True,
                    'quality_improved': True
                })
                processed += 1
                print(f"   ✅ 저장 완료")
                
            except Exception as e:
                errors += 1
                print(f"   ❌ 저장 실패: {e}")
        
        else:
            errors += 1
            print(f"   ❌ 변환 실패: {result['error']}")
        
        # API 제한 방지
        time.sleep(2)
    
    print(f"\n{'=' * 80}")
    print(f"✅ 처리 완료: {processed}개")
    print(f"❌ 오류: {errors}개")
    print(f"{'=' * 80}")
    print(f"\n💡 JNext 통합 준비:")
    print(f"   - 프롬프트: FINAL_PUBLISHING_PROMPT")
    print(f"   - 함수: refine_to_final(doc_id, content, category)")
    print(f"   - 의도 키워드: '출판 변환', '문체 개선', 'final로'")

if __name__ == "__main__":
    process_problem_docs()
