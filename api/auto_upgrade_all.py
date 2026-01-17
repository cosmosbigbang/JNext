"""
전체 문서 자동 업그레이드 스크립트
1. AI 언급 변환: J님께서는 => J는, 진/젠/클로/지피 => 지피
2. 품질 분석 및 업그레이드
3. 같은 카테고리/운동 통합
4. draft 컬렉션으로 이동
"""
import firebase_admin
from firebase_admin import credentials, firestore
from collections import defaultdict
import re
from datetime import datetime
import google.generativeai as genai
import os

# Firebase 초기화
if not firebase_admin._apps:
    cred = credentials.Certificate('jnext-service-account.json')
    firebase_admin.initialize_app(cred)

db = firestore.client()

# Gemini 초기화
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-2.0-flash-exp')

def clean_ai_mentions(text):
    """AI 언급 변환"""
    if not text:
        return text
    
    # J님께서는 => J는
    text = re.sub(r'J님께서는', 'J는', text)
    text = re.sub(r'J님께서', 'J는', text)
    text = re.sub(r'J님이', 'J가', text)
    
    # AI 이름 => 지피
    ai_names = ['진', '젠', '젠하이', '클로', '지피']
    for name in ai_names:
        # 대화 형식에서는 "지피:"로 변환
        text = re.sub(rf'{name}:', '지피:', text)
        # 본문에서는 제거 또는 지피로 변환 (컨텍스트에 따라)
        text = re.sub(rf'\b{name}\b', '지피', text)
    
    return text

def get_all_documents(collection_path):
    """컬렉션의 모든 문서 가져오기"""
    try:
        docs = db.collection(collection_path).stream()
        result = []
        for doc in docs:
            data = doc.to_dict()
            data['doc_id'] = doc.id
            data['doc_ref'] = doc.reference
            result.append(data)
        return result
    except Exception as e:
        print(f"❌ 문서 로드 실패 ({collection_path}): {e}")
        return []

def group_documents(documents):
    """문서를 카테고리별로 그룹화"""
    groups = defaultdict(list)
    
    for doc in documents:
        # 카테고리 추출 (하이노이론 => 이론)
        category = doc.get('카테고리') or doc.get('category') or doc.get('제목', '')
        
        # 하이노이론 => 이론으로 변환
        if '하이노이론' in category:
            category = '이론'
        
        groups[category].append(doc)
    
    return groups

def analyze_and_upgrade(docs, category):
    """문서 분석 및 업그레이드"""
    print(f"\n{'='*70}")
    print(f"📝 {category} 카테고리 처리 중 ({len(docs)}개 문서)")
    print(f"{'='*70}")
    
    # 1. AI 언급 변환
    for doc in docs:
        if '제목' in doc:
            doc['제목'] = clean_ai_mentions(doc['제목'])
        if '내용' in doc:
            doc['내용'] = clean_ai_mentions(doc['내용'])
        if '전체글' in doc:
            doc['전체글'] = clean_ai_mentions(doc['전체글'])
        if 'content' in doc:
            doc['content'] = clean_ai_mentions(doc['content'])
        if 'title' in doc:
            doc['title'] = clean_ai_mentions(doc['title'])
    
    # 2. 같은 운동/이론이면 통합, 아니면 개별 업그레이드
    if len(docs) > 1:
        # 통합 필요 여부 판단 (exercise_name 또는 제목이 같으면)
        names = set()
        for doc in docs:
            name = doc.get('exercise_name') or doc.get('제목') or doc.get('title') or ''
            names.add(name.strip())
        
        if len(names) == 1:  # 모두 같은 운동/이론
            return merge_documents(docs, category, list(names)[0])
        else:  # 다른 문서들
            return upgrade_documents_separately(docs, category)
    else:  # 1개 문서
        return upgrade_single_document(docs[0], category)

def merge_documents(docs, category, name):
    """같은 운동/이론 문서들을 하나로 통합"""
    print(f"🔗 통합 작업: {name} ({len(docs)}개 문서)")
    
    # 모든 내용 병합
    all_content = []
    for doc in docs:
        content = doc.get('전체글') or doc.get('내용') or doc.get('content') or ''
        if content:
            all_content.append(f"## {doc.get('제목') or doc.get('title') or name}\n\n{content}")
    
    merged_content = "\n\n---\n\n".join(all_content)
    
    # AI 업그레이드 (통합 버전)
    prompt = f"""다음은 '{name}' ({category})에 대한 여러 문서를 병합한 내용입니다.
하이노밸런스 전체 맥락과 이 {category}의 특성을 살려서, 하나의 완성된 문서로 재작성해주세요.

변환 규칙:
- J님께서는 => J는
- 진/젠/클로/지피 => 지피
- 중복 내용 제거
- 논리적 흐름 개선
- 핵심 가치 강조

병합된 원본:
{merged_content}

재작성된 최종 문서:"""

    try:
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                temperature=0.3,
                max_output_tokens=8000
            )
        )
        upgraded_content = response.text
    except Exception as e:
        print(f"❌ AI 업그레이드 실패: {e}")
        upgraded_content = merged_content
    
    # draft 컬렉션에 저장
    result_doc = {
        'title': name,
        '제목': name,
        'content': upgraded_content,
        '내용': upgraded_content,
        '전체글': upgraded_content,
        'category': category,
        '카테고리': category,
        'doc_type': '이론' if category == '이론' else '실전',
        'exercise_name': name,
        'status': 'draft',
        'created_at': firestore.SERVER_TIMESTAMP,
        'updated_at': firestore.SERVER_TIMESTAMP,
        'source': 'auto_merged',
        'source_count': len(docs),
        '품질점수': 85,
        'ai모델': 'gemini-2.0-flash-exp'
    }
    
    print(f"✅ 통합 완료: {name}")
    return result_doc

def upgrade_documents_separately(docs, category):
    """문서들을 개별적으로 업그레이드"""
    results = []
    
    for doc in docs:
        upgraded = upgrade_single_document(doc, category)
        results.append(upgraded)
    
    return results

def upgrade_single_document(doc, category):
    """단일 문서 업그레이드"""
    name = doc.get('exercise_name') or doc.get('제목') or doc.get('title') or doc.get('doc_id')
    print(f"📄 개별 업그레이드: {name}")
    
    content = doc.get('전체글') or doc.get('내용') or doc.get('content') or ''
    
    # 이미 AI 언급은 변환됨
    # 품질 향상 업그레이드
    prompt = f"""다음은 '{name}' ({category})에 대한 문서입니다.
하이노밸런스 전체 맥락과 이 {category}의 특성을 살려서, 더 전문적이고 가치 있게 업그레이드해주세요.

변환 규칙:
- J님께서는 => J는
- 진/젠/클로/지피 => 지피
- 논리적 흐름 개선
- 핵심 가치 강조
- 전문성 향상

원본:
{content}

업그레이드된 문서:"""

    try:
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                temperature=0.3,
                max_output_tokens=8000
            )
        )
        upgraded_content = response.text
    except Exception as e:
        print(f"❌ AI 업그레이드 실패: {e}")
        upgraded_content = content
    
    # draft 컬렉션에 저장할 데이터
    result_doc = {
        'title': name,
        '제목': name,
        'content': upgraded_content,
        '내용': upgraded_content,
        '전체글': upgraded_content,
        'category': category,
        '카테고리': category,
        'doc_type': '이론' if category == '이론' else '실전',
        'exercise_name': name,
        'status': 'draft',
        'created_at': firestore.SERVER_TIMESTAMP,
        'updated_at': firestore.SERVER_TIMESTAMP,
        'source': 'auto_upgraded',
        '품질점수': 80,
        'ai모델': 'gemini-2.0-flash-exp'
    }
    
    print(f"✅ 업그레이드 완료: {name}")
    return result_doc

def save_to_draft(doc_data, category):
    """draft 컬렉션에 저장"""
    try:
        doc_id = f"{category}_{doc_data['exercise_name']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        doc_id = doc_id.replace(' ', '_').replace('/', '_')
        
        db.collection('projects/hinobalance/draft').document(doc_id).set(doc_data)
        print(f"💾 Draft 저장: {doc_id}")
        return True
    except Exception as e:
        print(f"❌ Draft 저장 실패: {e}")
        return False

def main():
    print(f"{'='*70}")
    print(f"🚀 전체 문서 자동 업그레이드 시작!")
    print(f"{'='*70}\n")
    
    # 1. raw 컬렉션 문서 로드
    print("📥 문서 로딩 중...")
    raw_docs = get_all_documents('projects/hinobalance/raw')
    print(f"✅ {len(raw_docs)}개 문서 로드 완료\n")
    
    if not raw_docs:
        print("❌ 문서가 없습니다!")
        return
    
    # 2. 카테고리별 그룹화
    groups = group_documents(raw_docs)
    print(f"📊 {len(groups)}개 카테고리로 그룹화:\n")
    for cat, docs in sorted(groups.items()):
        print(f"   - {cat}: {len(docs)}개")
    
    # 3. 카테고리별 처리
    total_success = 0
    total_fail = 0
    
    for category, docs in sorted(groups.items()):
        try:
            result = analyze_and_upgrade(docs, category)
            
            # 결과가 리스트면 여러 개, 딕셔너리면 1개
            if isinstance(result, list):
                for doc_data in result:
                    if save_to_draft(doc_data, category):
                        total_success += 1
                    else:
                        total_fail += 1
            else:
                if save_to_draft(result, category):
                    total_success += 1
                else:
                    total_fail += 1
                    
        except Exception as e:
            print(f"❌ {category} 처리 실패: {e}")
            total_fail += len(docs)
    
    # 4. 결과 출력
    print(f"\n{'='*70}")
    print(f"📊 작업 완료!")
    print(f"   ✅ 성공: {total_success}개")
    print(f"   ❌ 실패: {total_fail}개")
    print(f"   📂 raw 컬렉션: 유지 (삭제 안함)")
    print(f"   📂 draft 컬렉션: {total_success}개 추가")
    print(f"{'='*70}")

if __name__ == '__main__':
    main()
