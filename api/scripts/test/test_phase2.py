"""
JNext Phase 2 - 명령어 파싱 엔진 테스트 스크립트
"""

import requests
import json

# API 서버 주소
BASE_URL = "http://localhost:8000"
API_ENDPOINT = f"{BASE_URL}/api/v1/execute-command/"

# API Key (설정한 경우)
API_KEY = None  # 또는 "your-secret-api-key-here"

# 헤더 설정
headers = {
    "Content-Type": "application/json",
}
if API_KEY:
    headers["X-API-Key"] = API_KEY


def test_create():
    """CREATE 명령어 테스트"""
    print("\n=== TEST 1: CREATE ===")
    data = {
        "command": "CREATE_OR_UPDATE",
        "collection": "test_users",
        "payload": {
            "data": {
                "name": "홍길동",
                "email": "hong@example.com",
                "age": 25,
                "status": "active"
            }
        }
    }
    
    response = requests.post(API_ENDPOINT, json=data, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    # 생성된 문서 ID 반환
    if response.status_code == 200:
        return response.json().get('document_id')
    return None


def test_read_all():
    """READ 명령어 테스트 (전체 조회)"""
    print("\n=== TEST 2: READ ALL ===")
    data = {
        "command": "READ",
        "collection": "test_users",
        "payload": {}
    }
    
    response = requests.post(API_ENDPOINT, json=data, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")


def test_read_one(document_id):
    """READ 명령어 테스트 (특정 문서)"""
    if not document_id:
        print("\n=== TEST 3: SKIPPED (no document_id) ===")
        return
    
    print("\n=== TEST 3: READ ONE ===")
    data = {
        "command": "READ",
        "collection": "test_users",
        "payload": {
            "document_id": document_id
        }
    }
    
    response = requests.post(API_ENDPOINT, json=data, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")


def test_update(document_id):
    """UPDATE 명령어 테스트"""
    if not document_id:
        print("\n=== TEST 4: SKIPPED (no document_id) ===")
        return
    
    print("\n=== TEST 4: UPDATE ===")
    data = {
        "command": "CREATE_OR_UPDATE",
        "collection": "test_users",
        "payload": {
            "document_id": document_id,
            "data": {
                "age": 26,
                "status": "updated"
            }
        }
    }
    
    response = requests.post(API_ENDPOINT, json=data, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")


def test_read_with_filter():
    """READ 명령어 테스트 (필터 적용)"""
    print("\n=== TEST 5: READ WITH FILTER ===")
    data = {
        "command": "READ",
        "collection": "test_users",
        "payload": {
            "filters": {
                "status": "active"
            }
        }
    }
    
    response = requests.post(API_ENDPOINT, json=data, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")


def test_delete(document_id):
    """DELETE 명령어 테스트"""
    if not document_id:
        print("\n=== TEST 6: SKIPPED (no document_id) ===")
        return
    
    print("\n=== TEST 6: DELETE ===")
    data = {
        "command": "DELETE",
        "collection": "test_users",
        "payload": {
            "document_id": document_id
        }
    }
    
    response = requests.post(API_ENDPOINT, json=data, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")


if __name__ == "__main__":
    print("=" * 50)
    print("JNext Phase 2 API 테스트 시작")
    print("=" * 50)
    
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
    
    # 6. DELETE
    # test_delete(doc_id)  # 주석 해제하여 삭제 테스트
    
    print("\n" + "=" * 50)
    print("테스트 완료!")
    print("=" * 50)
