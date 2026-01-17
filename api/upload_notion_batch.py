"""
노션 Export 파일 → Firestore hino_raw 배치 업로드
자동 매칭된 15개 운동 업로드
"""
import os
import sys
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

# Firebase 초기화
if not firebase_admin._apps:
    cred = credentials.Certificate('jnext-service-account.json')
    firebase_admin.initialize_app(cred)

db = firestore.client()

# 매칭 테이블: {출시 운동명: (노션 파일명, 카테고리)}
MATCHING_TABLE = {
    # === 이론 카테고리 (하이노이론) ===
    # 이론 문서 (3개)
    '이론_최종241228': ('이론 최종241228 2d7d9ddff6ab8015b0f0ff0b866866d2.md', '하이노이론'),
    '이론_251228': ('이론 251228 2d7d9ddff6ab809a8da3d508a46d0450.md', '하이노이론'),
    '이론_개선260111': ('이론 개선 내용 260111 2e4d9ddff6ab80c7b779f6fe39f4f15d.md', '하이노이론'),
    
    # 밈 문서 (7개)
    '밈_251218': ('밈 251218 2ccd9ddff6ab80edb08cd87ec89a0c22.md', '하이노이론'),
    '밈_DB구조': ('밈 DB구조 2e1d9ddff6ab806b9adfe94ca6e93879.md', '하이노이론'),
    '밈_fk': ('밈 fk 2e1d9ddff6ab80bab216ca1c09c1d30a.md', '하이노이론'),
    '밈_가치평가': ('밈, 가치평가 251218 2ccd9ddff6ab805cae62fcef4f0f9ebb.md', '하이노이론'),
    '밈_탄생서사': ('지피와 탄생서사 밈 2ccd9ddff6ab800fa6a3fb04ae5f7da6.md', '하이노이론'),
    '밈_프리으싸': ('하이노프리, 으싸 밈,효과 2ccd9ddff6ab808e8db5e621f26640cc.md', '하이노이론'),
    '밈_스케이팅': ('스케이팅 정리 밈 251217 2ccd9ddff6ab8079bbb2fbbf725a0c4a.md', '하이노이론'),
    
    # 평가/가치 문서 (6개)
    '평가_하이노밸런스': ('하이노밸런스 평가•효과 251218 2ccd9ddff6ab80ce9543ed69ec8276d7.md', '하이노이론'),
    '평가_종합': ('종합평가 2e1d9ddff6ab80629101f6cb00707d05.md', '하이노이론'),
    '평가_지큐': ('지큐 평가 251225 2d3d9ddff6ab80028ff2de33c27f72f5.md', '하이노이론'),
    '평가_젠3대원리': ('젠 평가 3대원리 - 251221 2d0d9ddff6ab80389789f57aceb104e5.md', '하이노이론'),
    '가치_학문적운동학적': ('학문적•운동학적 가치 2dbd9ddff6ab80b2a261d1f4e4833df1.md', '하이노이론'),
    '가치_워킹소감': ('워킹 소감, 가치 2cdd9ddff6ab80399123c02575a12a7c.md', '하이노이론'),
    
    # 원리 문서 (3개)
    '원리_01': ('원리 01 2cdd9ddff6ab805bb65ce236f6d9e025.md', '하이노이론'),
    '원리_02': ('원리 02 2cdd9ddff6ab8040a19fe279c4703684.md', '하이노이론'),
    '원리_3대원리': ('젠 평가 3대원리 - 251221 2d0d9ddff6ab80389789f57aceb104e5.md', '하이노이론'),
    
    # 기타 이론 문서
    '이론_16개요점백업': ('16개 요점 백업 251217 2ccd9ddff6ab803d88f3dc2d8e1935ec.md', '하이노이론'),
    '이론_불균형의미': ('불균형의 의미 2cdd9ddff6ab80138d07f7595ab8f67e.md', '하이노이론'),
    '이론_가속도물리': ('가속도의 물리적 논리 2d3d9ddff6ab804eabd8f62a5ee23e71.md', '하이노이론'),
    '이론_계단의의미': ('계단 내려오는거의 의미 2cfd9ddff6ab80f2a314e55d47e2182b.md', '하이노이론'),
    '이론_하이노의미': ('하이노 의미251217 2ccd9ddff6ab80a9bb23c67b65c5d67a.md', '하이노이론'),
    '이론_딥싱크분석': ('딥싱크 분석 2d4d9ddff6ab80febf8bf78c1ee5f234.md', '하이노이론'),
    
    # === 운동 카테고리 ===
    # 워밍 (2개) - 같은 파일이지만 내용 다르게 추출
    '하이노워밍벤치': ('하이노으싸앞으로벤치 2cdd9ddff6ab8079a663cacc4755718b.md', '하이노워밍'),
    
    # 골반 (4개) - 하나의 파일에 4개 동작 포함
    '하이노골반상하': ('하이노골반 2e1d9ddff6ab807abdabebdd663140d6.md', '하이노골반'),
    '하이노골반좌우': ('하이노골반 2e1d9ddff6ab807abdabebdd663140d6.md', '하이노골반'),
    '하이노골반돌리기': ('하이노골반 2e1d9ddff6ab807abdabebdd663140d6.md', '하이노골반'),
    '하이노골반벌리기': ('하이노골반 2e1d9ddff6ab807abdabebdd663140d6.md', '하이노골반'),
    
    # 워킹 (4개)
    '하이노워킹전진': ('하이노워킹 - 기본 2cdd9ddff6ab8000b1b7f1e2914d280f.md', '하이노워킹'),
    '하이노워킹주먹': ('패스트, 주먹 2cdd9ddff6ab80f683c6d98927e77b99.md', '하이노워킹'),
    '하이노워킹크로스': ('하이노워킹크로스 2cdd9ddff6ab80718f6cd7575d81e650.md', '하이노워킹'),
    '하이노워킹퐁당퐁당': ('퐁당퐁당, 닭싸움 2cdd9ddff6ab8099b98ae9df86e2388d.md', '하이노워킹'),
    
    # 스케이팅 (3개)
    '하이노스케이팅좌우': ('하이노스케이팅좌우 2dad9ddff6ab8029a099c5b492172e1e.md', '하이노스케이팅'),
    '하이노스케이팅전진': ('하이노스케이팅전진 2d8d9ddff6ab80919102c16f7624dbb4.md', '하이노스케이팅'),
    '하이노스케이팅코너웍': ('스케이팅 정리 밈 251217 2ccd9ddff6ab8079bbb2fbbf725a0c4a.md', '하이노스케이팅'),
    
    # 풋삽 (2개)
    '하이노풋삽벽두손': ('하이노전신근력 정리 251217 2ccd9ddff6ab80c5bc46e974bd595ea2.md', '하이노풋삽'),
    '하이노풋삽벽한손': ('하이노전신근력 정리 251217 2ccd9ddff6ab80c5bc46e974bd595ea2.md', '하이노풋삽'),
    
    # 철봉 (1개)
    '하이노철봉한손': ('하이노철봉한손 2cad9ddff6ab808984e8ed062839b119.md', '하이노철봉'),
}

def read_notion_file(filename):
    """노션 파일 읽기"""
    filepath = os.path.join('notion', filename)
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except FileNotFoundError:
        print(f"❌ 파일 없음: {filename}")
        return None
    except Exception as e:
        print(f"❌ 파일 읽기 오류 ({filename}): {e}")
        return None

def extract_title_and_content(content, exercise_name):
    """제목과 내용 분리"""
    if not content:
        return exercise_name, ""
    
    lines = content.split('\n')
    
    # 첫 번째 # 제목 찾기
    title = exercise_name  # 기본값
    for line in lines:
        if line.startswith('# ') and not line.startswith('## '):
            title = line.replace('# ', '').strip()
            break
    
    return title, content

def upload_to_firestore(exercise_name, filename, category):
    """Firestore에 업로드"""
    print(f"\n📤 {exercise_name} 업로드 중...")
    
    # 파일 읽기
    content = read_notion_file(filename)
    if not content:
        return False
    
    # 제목/내용 추출
    title, full_content = extract_title_and_content(content, exercise_name)
    
    # 문서 타입 결정 (이론 vs 실전)
    doc_type = "이론" if category == "하이노이론" else "실전"
    
    # Firestore 문서 생성
    doc_data = {
        'title': title,
        'content': full_content,
        'doc_type': doc_type,  # 이론/실전 구분
        'category': category,
        'exercise_name': exercise_name,
        'source': 'notion',
        'source_file': filename,
        'created_at': firestore.SERVER_TIMESTAMP,
        'updated_at': firestore.SERVER_TIMESTAMP,
        'status': 'raw'  # raw 상태로 시작
    }
    
    # hino_raw 컬렉션에 추가
    try:
        doc_ref = db.collection('hino_raw').document(exercise_name)
        doc_ref.set(doc_data)
        print(f"✅ {exercise_name} 업로드 완료! (카테고리: {category})")
        print(f"   파일: {filename}")
        return True
    except Exception as e:
        print(f"❌ {exercise_name} 업로드 실패: {e}")
        return False

def main():
    print("=" * 70)
    print("🚀 노션 Export → Firestore hino_raw 배치 업로드 시작!")
    print("=" * 70)
    
    success_count = 0
    fail_count = 0
    
    for exercise_name, (filename, category) in MATCHING_TABLE.items():
        if upload_to_firestore(exercise_name, filename, category):
            success_count += 1
        else:
            fail_count += 1
    
    print("\n" + "=" * 70)
    print(f"📊 업로드 완료!")
    print(f"   ✅ 성공: {success_count}개")
    print(f"   ❌ 실패: {fail_count}개")
    print("=" * 70)
    
    # 카테고리별 통계
    print("\n📂 카테고리별 업로드:")
    categories = {}
    for _, (_, category) in MATCHING_TABLE.items():
        categories[category] = categories.get(category, 0) + 1
    for cat, count in sorted(categories.items()):
        print(f"   {cat}: {count}개")
    
    # 수동 정리 필요한 운동 안내
    print("\n⚠️  J님이 수동으로 정리하실 운동 (3개):")
    print("  1. 하이노워밍기본 (대화로 AI 정리)")
    print("  2. 하이노스케이팅후진 (대화로 AI 정리)")
    print("  3. 하이노철봉두손 (대화로 AI 정리)")
    print("\n💡 대화로 설명하시면 제가 정리해서 raw 저장해드릴게요!")
    
    return success_count, fail_count

if __name__ == '__main__':
    try:
        success, fail = main()
        sys.exit(0 if fail == 0 else 1)
    except Exception as e:
        print(f"\n❌ 치명적 오류: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
