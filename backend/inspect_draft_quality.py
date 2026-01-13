"""
hino_draft 전수 검사 - 출판 적합성 분석
"""
import firebase_admin
from firebase_admin import credentials, firestore
from pathlib import Path
import re

# Firebase 초기화
if not firebase_admin._apps:
    base_dir = Path(__file__).resolve().parent
    cred_path = base_dir.parent / 'jnext-service-account.json'
    cred = credentials.Certificate(str(cred_path))
    firebase_admin.initialize_app(cred)

db = firestore.client()

def analyze_quality(content: str) -> dict:
    """문체 품질 분석"""
    
    # 기본 통계
    char_count = len(content)
    lines = content.split('\n')
    non_empty_lines = [l for l in lines if l.strip()]
    
    # 문장 분석
    sentences = re.split(r'[.!?]\s*', content)
    sentences = [s for s in sentences if len(s.strip()) > 5]
    
    # 평균 문장 길이
    avg_sentence_length = sum(len(s) for s in sentences) / len(sentences) if sentences else 0
    
    # 짧은 문장 비율 (15자 이하)
    short_sentences = [s for s in sentences if len(s) <= 15]
    short_ratio = len(short_sentences) / len(sentences) if sentences else 0
    
    # "~이다", "~한다" 반복 패턴
    ending_patterns = {
        '이다': len(re.findall(r'이다[.\s]', content)),
        '한다': len(re.findall(r'한다[.\s]', content)),
        '있다': len(re.findall(r'있다[.\s]', content)),
        '된다': len(re.findall(r'된다[.\s]', content)),
    }
    
    total_patterns = sum(ending_patterns.values())
    pattern_density = total_patterns / len(sentences) if sentences else 0
    
    # 불릿 포인트 사용
    bullet_count = content.count('*   ')
    
    # 여백 (연속 줄바꿈)
    empty_line_blocks = len(re.findall(r'\n\n+', content))
    
    # 굵게 강조
    bold_count = content.count('**') // 2
    
    # 문제점 판단
    issues = []
    
    if short_ratio > 0.7:
        issues.append(f"⚠️ 짧은 문장 과다 ({short_ratio*100:.0f}%)")
    
    if pattern_density > 0.8:
        issues.append(f"⚠️ 단조로운 종결어미 ({pattern_density*100:.0f}%)")
    
    if avg_sentence_length < 10:
        issues.append(f"⚠️ 평균 문장 너무 짧음 ({avg_sentence_length:.1f}자)")
    
    if bullet_count > len(sentences) * 0.3:
        issues.append(f"⚠️ 불릿 포인트 과다 ({bullet_count}개)")
    
    if bold_count > 5:
        issues.append(f"⚠️ 굵게 강조 남음 ({bold_count}회)")
    
    return {
        'char_count': char_count,
        'sentence_count': len(sentences),
        'avg_length': avg_sentence_length,
        'short_ratio': short_ratio,
        'pattern_density': pattern_density,
        'ending_patterns': ending_patterns,
        'bold_count': bold_count,
        'bullet_count': bullet_count,
        'issues': issues,
        'quality_score': calculate_score(short_ratio, pattern_density, avg_sentence_length, bold_count)
    }

def calculate_score(short_ratio, pattern_density, avg_length, bold_count):
    """품질 점수 계산 (100점 만점)"""
    score = 100
    
    # 짧은 문장 과다 (-30점)
    if short_ratio > 0.7:
        score -= 30
    elif short_ratio > 0.5:
        score -= 15
    
    # 단조로운 종결어미 (-30점)
    if pattern_density > 0.8:
        score -= 30
    elif pattern_density > 0.6:
        score -= 15
    
    # 문장 길이 (-20점)
    if avg_length < 10:
        score -= 20
    elif avg_length < 15:
        score -= 10
    
    # 굵게 강조 남음 (-20점)
    if bold_count > 5:
        score -= 20
    elif bold_count > 2:
        score -= 10
    
    return max(0, score)

def inspect_all_drafts():
    """모든 draft 검사"""
    
    print("=" * 100)
    print("HINO_DRAFT 전수 검사 - 출판 적합성 분석")
    print("=" * 100)
    
    draft_ref = db.collection('hino_draft')
    docs = draft_ref.order_by('created_at').stream()
    
    results = []
    
    for doc in docs:
        data = doc.to_dict()
        doc_id = doc.id
        
        if 'content' not in data or not isinstance(data['content'], str):
            continue
        
        content = data['content']
        category = data.get('category', 'unknown')
        content_type = data.get('content_type', 'unknown')
        
        analysis = analyze_quality(content)
        
        results.append({
            'id': doc_id,
            'category': category,
            'type': content_type,
            'analysis': analysis
        })
    
    # 결과 출력
    for r in results:
        print(f"\n{'=' * 100}")
        print(f"📄 {r['id']}")
        print(f"   카테고리: {r['category']} / 타입: {r['type']}")
        print(f"{'=' * 100}")
        
        a = r['analysis']
        
        print(f"\n📊 기본 통계:")
        print(f"   • 전체 길이: {a['char_count']:,}자")
        print(f"   • 문장 수: {a['sentence_count']}개")
        print(f"   • 평균 문장 길이: {a['avg_length']:.1f}자")
        print(f"   • 짧은 문장 비율: {a['short_ratio']*100:.0f}%")
        
        print(f"\n📝 문체 분석:")
        print(f"   • 종결어미 패턴:")
        for pattern, count in a['ending_patterns'].items():
            print(f"     - '{pattern}': {count}회")
        print(f"   • 패턴 밀도: {a['pattern_density']*100:.0f}%")
        print(f"   • 굵게 강조: {a['bold_count']}회")
        print(f"   • 불릿 포인트: {a['bullet_count']}개")
        
        print(f"\n⚖️  품질 점수: {a['quality_score']}/100")
        
        if a['issues']:
            print(f"\n🚨 문제점:")
            for issue in a['issues']:
                print(f"   {issue}")
        else:
            print(f"\n✅ 양호")
        
        # 미리보기
        preview = content[:200].replace('\n', ' ')
        print(f"\n📖 미리보기:")
        print(f"   {preview}...")
    
    # 전체 요약
    print(f"\n\n{'=' * 100}")
    print("📊 전체 요약")
    print(f"{'=' * 100}")
    
    total = len(results)
    good = len([r for r in results if r['analysis']['quality_score'] >= 70])
    moderate = len([r for r in results if 40 <= r['analysis']['quality_score'] < 70])
    poor = len([r for r in results if r['analysis']['quality_score'] < 40])
    
    print(f"\n총 문서 수: {total}개")
    print(f"✅ 양호 (70점 이상): {good}개")
    print(f"⚠️  보통 (40-69점): {moderate}개")
    print(f"❌ 불량 (40점 미만): {poor}개")
    
    avg_score = sum(r['analysis']['quality_score'] for r in results) / total if total > 0 else 0
    print(f"\n평균 품질: {avg_score:.1f}/100")
    
    print(f"\n{'=' * 100}")

if __name__ == "__main__":
    inspect_all_drafts()
