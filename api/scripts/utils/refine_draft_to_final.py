"""
hino_draft → 출판용 문체로 재정리
J님의 출판 가이드 적용:
- 굵게 강조 최소화 (챕터당 1~2회)
- 선언형 문체
- 짧은 문장, 줄바꿈, 여백
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
    base_dir = Path(__file__).resolve().parent
    cred_path = base_dir / 'jnext-service-account.json'
    cred = credentials.Certificate(str(cred_path))
    firebase_admin.initialize_app(cred)

db = firestore.client()

# Gemini API 설정
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-2.0-flash-exp')

# 출판 가이드 프롬프트
PUBLISHING_GUIDE = """
# 하이노밸런스 이론 - 출판용 문체 변환 가이드

## 핵심 원칙

1. **굵게 강조 최소화**
   - 챕터당 1~2회만 허용
   - 개념 설명 중 굵게 전면 제거
   - 현재 과다 사용된 ** ** 제거

2. **강조 방식 변경**
   - 굵게 대신:
     * 짧은 문장
     * 줄바꿈
     * 여백
     * 단정형 선언문

3. **문체 방향**
   - ❌ 설명형 ("~입니다", "~할 수 있습니다")
   - ❌ 학술형 ("~에 대해", "~라고 볼 수 있다")
   - ✅ 선언형 ("~이다", "~한다")
   - ✅ 철학·원리 제시형

4. **독자 관계**
   - "가르친다" ❌
   - "이미 알고 있는 진실을 정리해준다" ✅

5. **출판 목표**
   - 읽는 순간 신뢰가 생기는 글
   - "운동 설명서"가 아니라 "운동 철학 + 신체 사용 매뉴얼"

## 변환 예시

**Before (과잉 강조):**
하이노밸런스는 **단순한 운동이 아닙니다**. 이것은 **신경계를 활성화**하고 **뇌를 깨우는** 혁신적인 방법입니다. **가속도의 법칙**을 활용하여 **균형 감각**을 향상시킵니다.

**After (출판 문체):**
하이노밸런스는 운동이 아니다.
신경계를 깨우는 방법이다.

가속도가 뇌를 자극한다.
불균형이 균형을 만든다.

이것은 철학이다.

---

## 당신의 임무

주어진 텍스트를 위 가이드에 따라 변환하시오.
- 내용의 본질은 유지
- 굵게 강조 최소화
- 선언형·철학적 문체로 변경
- 짧은 문장과 여백 활용

변환된 텍스트만 출력하시오. 설명 불필요.
"""

def refine_content(content: str, category: str) -> str:
    """Gemini API로 콘텐츠 재정리"""
    prompt = f"{PUBLISHING_GUIDE}\n\n## 원본 텍스트\n\n{content}"
    
    try:
        response = model.generate_content(
            prompt,
            generation_config={
                'temperature': 0.3,  # 정확성 우선
                'top_p': 0.8,
                'top_k': 40,
                'max_output_tokens': 8192,
            }
        )
        
        refined = response.text.strip()
        return refined
        
    except Exception as e:
        print(f"  ⚠️  Gemini API 오류: {e}")
        return content  # 실패 시 원본 반환

def process_all_drafts():
    """모든 draft 문서 처리"""
    
    print("=" * 80)
    print("HINO_DRAFT → 출판용 문체 변환")
    print("=" * 80)
    
    # draft 문서 조회 (content 필드 있는 것만)
    draft_ref = db.collection('hino_draft')
    docs = draft_ref.order_by('created_at').stream()
    
    processed = 0
    skipped = 0
    errors = 0
    
    for doc in docs:
        data = doc.to_dict()
        doc_id = doc.id
        
        # content 필드 없으면 스킵
        if 'content' not in data or not isinstance(data['content'], str):
            skipped += 1
            print(f"\n⏭️  스킵: {doc_id} (content 없음)")
            continue
        
        content = data['content']
        category = data.get('category', 'unknown')
        content_type = data.get('content_type', 'unknown')
        
        # 굵게 사용 횟수
        bold_count = content.count('**') // 2
        
        print(f"\n{'=' * 80}")
        print(f"📄 {doc_id}")
        print(f"   카테고리: {category}")
        print(f"   타입: {content_type}")
        print(f"   굵게: {bold_count}회")
        print(f"   길이: {len(content):,}자")
        
        # 굵게가 적으면 스킵 (5회 이하)
        if bold_count <= 5:
            skipped += 1
            print(f"   ✅ 양호 (굵게 {bold_count}회만 사용)")
            continue
        
        # Gemini API로 재정리
        print(f"   🔄 재정리 중...")
        refined_content = refine_content(content, category)
        
        # 굵게 사용 횟수 비교
        new_bold_count = refined_content.count('**') // 2
        print(f"   📊 굵게: {bold_count}회 → {new_bold_count}회")
        
        # Firestore 업데이트
        try:
            doc.reference.update({
                'content': refined_content,
                'updated_at': firestore.SERVER_TIMESTAMP,
                'refined': True,
                'original_bold_count': bold_count,
                'refined_bold_count': new_bold_count
            })
            processed += 1
            print(f"   ✅ 저장 완료")
            
        except Exception as e:
            errors += 1
            print(f"   ❌ 저장 실패: {e}")
        
        # API 제한 방지
        time.sleep(1)
    
    print(f"\n{'=' * 80}")
    print(f"✅ 처리 완료: {processed}개")
    print(f"⏭️  스킵: {skipped}개")
    print(f"❌ 오류: {errors}개")
    print(f"{'=' * 80}")

if __name__ == "__main__":
    process_all_drafts()
