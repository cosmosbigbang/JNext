"""
J님 최종 시나리오 테스트
세션 유지하면서 테스트
"""
import requests
import json

BASE_URL = "https://jnext.onrender.com"

def test_scenario():
    """
    시나리오 (세션 유지):
    1. "하이노밸런스 이론 정리해" → ORGANIZE (AI 응답)
    2. "db에 저장해" → SAVE (모달창)
    """
    
    print("=" * 60)
    print("J님 최종 시나리오 테스트 (세션 유지)")
    print("=" * 60)
    
    # 세션 생성 (쿠키 유지)
    session = requests.Session()
    
    # Step 1: AI 응답 생성
    print("\n[Step 1] AI 응답: '하이노밸런스 이론 정리해'")
    response1 = session.post(
        f"{BASE_URL}/api/v1/chat/",
        json={
            "message": "하이노밸런스 이론 정리해",
            "mode": "organize",
            "model": "gemini-flash"
        },
        timeout=30
    )
    print(f"Status: {response1.status_code}")
    data1 = response1.json()
    print(f"Action: {data1.get('action')}")
    print(f"DB 문서 수: {data1.get('db_documents_count', 0)}")
    print(f"응답: {data1['response']['answer'][:200]}...")
    
    # Step 2: 저장 (같은 세션)
    print("\n[Step 2] 저장: 'db에 저장해' (같은 세션)")
    response2 = session.post(
        f"{BASE_URL}/api/v1/chat/",
        json={
            "message": "db에 저장해",
            "mode": "organize",
            "model": "gemini-flash"
        },
        timeout=30
    )
    print(f"Status: {response2.status_code}")
    data2 = response2.json()
    print(f"Action: {data2.get('action')}")
    
    # 모달창 데이터 확인
    if 'save_data' in data2:
        print("✅ 모달창 데이터 준비됨:")
        save_data = data2['save_data']
        print(f"  - 제목: {save_data.get('title', 'N/A')}")
        print(f"  - 카테고리: {save_data.get('category', 'N/A')}")
        print(f"  - 컬렉션: {save_data.get('collection', 'N/A')}")
        print(f"  - 내용 길이: {len(save_data.get('content', ''))}자")
        print("\n✅ 성공! 모달창이 정상적으로 띄워집니다!")
    else:
        print("❌ 모달창 데이터 없음")
        print(f"응답: {json.dumps(data2, ensure_ascii=False, indent=2)}")
    
    print("\n" + "=" * 60)
    print("테스트 완료!")
    print("=" * 60)

if __name__ == "__main__":
    try:
        test_scenario()
    except requests.exceptions.Timeout:
        print("❌ 타임아웃: Render 서버 응답 없음 (Cold Start일 수 있음)")
    except Exception as e:
        print(f"❌ 에러: {e}")
