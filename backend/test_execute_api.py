"""
JNext Phase 2-2 - 통합 Execute API 테스트 스크립트 (Gen 대화창용)
"""

import requests
import json

# API 서버 주소
BASE_URL = "http://localhost:8000"
API_ENDPOINT = f"{BASE_URL}/api/v1/execute/"

# API Key (설정한 경우)
API_KEY = None  # 또는 "your-secret-api-key-here"

# 헤더 설정
headers = {
    "Content-Type": "application/json",
}
if API_KEY:
    headers["X-API-Key"] = API_KEY


def test_create():
    """CREATE 액션 테스트"""
    print("\n=== TEST 1: CREATE ===")
    data = {
        "action": "CREATE",
        "collection": "gen_messages",
        "payload": {
            "user": "J님",
            "message": "안녕하세요! Gen입니다.",
            "type": "greeting",
            "priority": "high"
        }
    }
    
    response = requests.post(API_ENDPOINT, json=data, headers=headers)
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Response: {json.dumps(result, indent=2, ensure_ascii=False)}")
    
    # 생성된 문서 ID 반환
    if response.status_code == 200:
        return result.get('document_id')
    return None


def test_read_all():
    """READ 액션 테스트 (전체 조회)"""
    print("\n=== TEST 2: READ ALL ===")
    data = {
        "action": "READ",
        "collection": "gen_messages",
        "payload": {}
    }
    
    response = requests.post(API_ENDPOINT, json=data, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")


def test_read_one(document_id):
    """READ 액션 테스트 (특정 문서)"""
    if not document_id:
        print("\n=== TEST 3: SKIPPED (no document_id) ===")
        return
    
    print("\n=== TEST 3: READ ONE ===")
    data = {
        "action": "READ",
        "collection": "gen_messages",
        "document_id": document_id,
        "payload": {}
    }
    
    response = requests.post(API_ENDPOINT, json=data, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")


def test_update(document_id):
    """UPDATE 액션 테스트"""
    if not document_id:
        print("\n=== TEST 4: SKIPPED (no document_id) ===")
        return
    
    print("\n=== TEST 4: UPDATE ===")
    data = {
        "action": "UPDATE",
        "collection": "gen_messages",
        "document_id": document_id,
        "payload": {
            "priority": "normal",
            "processed": True
        }
    }
    
    response = requests.post(API_ENDPOINT, json=data, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")


def test_read_with_filter():
    """READ 액션 테스트 (필터 적용)"""
    print("\n=== TEST 5: READ WITH FILTER ===")
    data = {
        "action": "READ",
        "collection": "gen_messages",
        "payload": {
            "filters": {
                "type": "greeting"
            }
        }
    }
    
    response = requests.post(API_ENDPOINT, json=data, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")


def test_delete(document_id):
    """DELETE 액션 테스트"""
    if not document_id:
        print("\n=== TEST 6: SKIPPED (no document_id) ===")
        return
    
    print("\n=== TEST 6: DELETE ===")
    data = {
        "action": "DELETE",
        "collection": "gen_messages",
        "document_id": document_id,
        "payload": {}
    }
    
    response = requests.post(API_ENDPOINT, json=data, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")


if __name__ == "__main__":
    print("=" * 60)
    print("JNext Phase 2-2 통합 Execute API 테스트 (Gen 대화창용)")
    print("=" * 60)
    
    # 1. CREATE
    doc_id = test_create()
    
    # 2. READ ALL
    test_read_all()
    
    # 3. READ ONE
    test_read_one(doc_id)
    
    # 4. UPDATE
    test_update(doc_id)
    
    # 5. READ WITH FILTER
    test_read_with_filter()
    
    # 6. DELETE (주석 해제하여 삭제 테스트)
    # test_delete(doc_id)
    
    print("\n" + "=" * 60)
    print("테스트 완료!")
    print("Firebase Console: https://console.firebase.google.com/project/jnext-e3dd9/firestore")
    print("gen_messages 컬렉션을 확인하세요!")
    print("=" * 60)
