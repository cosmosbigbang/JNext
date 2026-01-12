"""
J님 피드백 반영 - 하이노철봉한손 재정리
"""
import firebase_admin
from firebase_admin import credentials, firestore
from pathlib import Path
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

if not firebase_admin._apps:
    base_dir = Path(__file__).resolve().parent
    cred_path = base_dir / 'jnext-service-account.json'
    cred = credentials.Certificate(str(cred_path))
    firebase_admin.initialize_app(cred)

db = firestore.client()
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-2.0-flash-exp')

# J님 피드백
J_FEEDBACK = """
# 하이노철봉한손 운동 - 핵심 수정사항

## 현재 문제
문서가 "한손으로만 철봉 잡기"로 오해하고 작성됨.

## 진짜 원리
- **한손 + 반대발 협업 운동**
- 예: 오른손 + 왼발 / 왼손 + 오른발
- **X자 사슬 가동** (대각선 연결)
- 손이 떨리면 → 하체 힘으로 버팀
- 전신 협업: 어깨부터 발목까지
- 매일 운동 가능, 금방 성장

## 핵심 차별점
- 한손만 X → 한손+반대발 협업 ✓
- 불균형만 강조 X → X자 사슬 핵심 ✓
- 상체 운동 X → 전신 협업 ✓

이 핵심을 중심으로 전체 내용을 재구성하시오.
"""

REVISION_PROMPT = """
# 하이노철봉한손 운동 재정리 (J님 피드백 반영)

당신은 운동 전문가이자 철학자입니다.
J님의 피드백을 받아 핵심을 재정리합니다.

""" + J_FEEDBACK + """

## 작업 지침

1. **핵심 강조**: X자 사슬 협업
2. **구조 재편**: 한손+반대발 중심
3. **출판 문체**: 자연스럽고 깊이 있게
4. **철학 통합**: 불균형 → X자 협업 → 전신 통합

원본 내용을 읽고, 위 피드백을 반영하여 완전히 재작성하시오.
변환된 텍스트만 출력. 설명 불필요.

---

## 원본 문서

"""

# 하이노철봉한손 문서 ID
doc_id = 'HKKJBZkwnyn6z8878Uhr'

print("=" * 80)
print("하이노철봉한손 재정리 (J님 피드백)")
print("=" * 80)

draft_ref = db.collection('hino_draft')
doc = draft_ref.document(doc_id).get()

if doc.exists:
    data = doc.to_dict()
    original = data['content']
    
    print(f"\n📄 원본 길이: {len(original):,}자")
    print(f"🔄 젠에게 피드백 전달 및 재정리 요청...\n")
    
    prompt = REVISION_PROMPT + original
    
    try:
        response = model.generate_content(
            prompt,
            generation_config={
                'temperature': 0.5,
                'top_p': 0.9,
                'top_k': 40,
                'max_output_tokens': 8192,
            }
        )
        
        revised = response.text.strip()
        
        print(f"✅ 재정리 완료")
        print(f"📊 결과: {len(revised):,}자")
        
        # Firestore 업데이트
        doc.reference.update({
            'content': revised,
            'updated_at': firestore.SERVER_TIMESTAMP,
            'j_feedback_applied': True,
            'revision_note': 'X자 사슬 협업 핵심 반영'
        })
        
        print(f"💾 Firestore 저장 완료")
        print(f"\n{'=' * 80}")
        print(f"💡 JNext 워크플로우 프로토타입 성공!")
        print(f"   J님 수정 → 클로 명령 → 젠 재정리 → 저장")
        print(f"{'=' * 80}")
        
    except Exception as e:
        print(f"❌ 오류: {e}")

else:
    print(f"❌ 문서 없음: {doc_id}")
