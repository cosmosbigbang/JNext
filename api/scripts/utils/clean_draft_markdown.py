"""
Draft 컬렉션 마크다운 특수문자 제거 및 내용 분석
Gemini API 사용
"""
import os
import sys
from pathlib import Path

# Django 설정 로드
api_path = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(api_path))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from firebase_admin import firestore
from django.conf import settings
from google.genai import types
import re
import time

db = firestore.client()

def remove_markdown(text):
    """마크다운 특수문자 제거"""
    if not text:
        return text
    
    # **볼드** 제거
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
    
    # *이탤릭* 제거
    text = re.sub(r'\*([^*]+)\*', r'\1', text)
    
    # ### 헤더 제거 (줄 시작)
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    
    # ` 코드 ` 제거
    text = re.sub(r'`([^`]+)`', r'\1', text)
    
    # > 인용 제거
    text = re.sub(r'^>\s+', '', text, flags=re.MULTILINE)
    
    # - 리스트 제거
    text = re.sub(r'^[\*\-]\s+', '', text, flags=re.MULTILINE)
    
    # 연속 공백 정리
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return text.strip()


def analyze_with_gemini(content, title):
    """Gemini로 내용 분석 및 개선"""
    
    client = settings.AI_MODELS['gemini-flash']['client']
    model_name = settings.AI_MODELS['gemini-flash']['model']
    
    prompt = f"""다음 하이노밸런스 문서를 전자책 출판용으로 개선하세요.

제목: {title}

원본 내용:
{content}

요구사항:
1. 마크다운 특수문자 완전 제거 (**, ###, >, -, * 등)
2. 자연스러운 문장 흐름 (단조로운 "~이다" 반복 지양)
3. 문장 리듬 다양화 (짧은/중간/긴 문장 섞기)
4. 전문성과 깊이 유지
5. 숫자 목록(1. 2. 3.)은 유지 가능
6. 하이노밸런스 철학 반영

개선된 내용만 출력하세요 (설명 없이):"""

    response = client.models.generate_content(
        model=model_name,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.7,
            max_output_tokens=4096
        )
    )
    
    return response.text.strip()


def process_draft_collection():
    """draft 컬렉션 전체 처리"""
    
    # projects/hinobalance/draft 확인
    draft_ref = db.collection('projects').document('hinobalance').collection('draft')
    docs = list(draft_ref.stream())
    
    print(f"\n{'='*60}")
    print(f"📝 Draft 컬렉션 마크다운 제거 및 분석")
    print(f"{'='*60}\n")
    print(f"총 {len(docs)}개 문서 발견\n")
    
    if len(docs) == 0:
        print("❌ draft 컬렉션이 비어있습니다.")
        return
    
    for idx, doc in enumerate(docs, 1):
        data = doc.to_dict()
        doc_id = doc.id
        title = data.get('제목', data.get('운동명', 'Unknown'))
        
        print(f"\n[{idx}/{len(docs)}] 처리 중: {title}")
        print(f"  문서 ID: {doc_id}")
        
        # 원본 내용
        original_content = data.get('전체글', data.get('내용', ''))
        
        if not original_content:
            print("  ⚠️  내용 없음 - 스킵")
            continue
        
        print(f"  원본 길이: {len(original_content)}자")
        
        # 1단계: 마크다운 제거
        cleaned_content = remove_markdown(original_content)
        print(f"  정리 후: {len(cleaned_content)}자")
        
        # 2단계: Gemini 분석 및 개선
        print("  🤖 Gemini 분석 중...")
        try:
            improved_content = analyze_with_gemini(cleaned_content, title)
            print(f"  개선 완료: {len(improved_content)}자")
            
            # 3단계: Firestore 업데이트
            update_data = {}
            
            if '전체글' in data:
                update_data['전체글'] = improved_content
            elif '내용' in data:
                update_data['내용'] = improved_content
            
            # 메타데이터 추가
            update_data['마크다운제거'] = True
            update_data['개선일시'] = firestore.SERVER_TIMESTAMP
            update_data['개선모델'] = 'gemini-flash'
            
            draft_ref.document(doc_id).update(update_data)
            print(f"  ✅ 업데이트 완료")
            
            # API 제한 고려 (1초 대기)
            time.sleep(1)
            
        except Exception as e:
            print(f"  ❌ 오류: {str(e)}")
            continue
    
    print(f"\n{'='*60}")
    print(f"🎉 처리 완료!")
    print(f"{'='*60}\n")


if __name__ == '__main__':
    process_draft_collection()
