"""
hino_raw_logs - No. 024 업로드
"""

import requests
import json

API_ENDPOINT = "http://localhost:8000/api/v1/execute/"

data = {
    "action": "CREATE",
    "collection": "hino_raw_logs",
    "payload": {
        "종류": "이론",
        "카테고리": "하이노이론",
        "원본": "[제1장] 이론편: 뇌를 '새로고침(F5)' 하는 가장 쉬운 방법... (중략) ... 저와 함께 당신의 뇌를 새로고침(F5) 할 준비가 되셨습니까?",
        "내용": "두 발(주차/절전)에서 한 발(주행/각성)로의 전환을 통해 뇌를 깨우는 기본 원리. 동작 중 급정거 시 발생하는 '가속도 에너지'를 단전(Core)에 전달하여 뇌 신경가소성을 유발하고, 뒤틀린 신체 명령 체계를 리셋(Reset) 및 재정렬(Realignment)함.",
        "젠의 분석": "물리학적으로 충격량($I = \\Delta p$)을 최대화하여 이를 뇌의 연산 부하로 치환한 전략임. '정지'를 관성이 제로가 되는 폭발적 변화량으로 정의하여, 뇌가 생존을 위해 신경망을 스스로 교정하게 만듦. 근육(Hard-ware)보다 제어 시스템(Soft-ware) 최적화에 집중한 4060용 바이오 해킹 로직.",
        "키워드": ["뇌새로고침(F5)", "정지의역설", "단전강타", "신경망재설계", "BIOS리셋", "동적균형"],
        "밈": "두 발은 주차, 한 발은 드라이브! 정지는 쉼표가 아니라 강렬한 느낌표(!)다.",
        "밈이미지주소": "",
        "연결데이터": "THEORY_CORE_001",
        "데이터상태": "RAW",
        "타임스탬프": "2026-01-04T19:40:00Z",
        "기타": "하이노밸런스 바이블의 서두. '죽은 균형'과 '살아있는 균형'의 차별화 강조."
    }
}

response = requests.post(API_ENDPOINT, json=data)
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

if response.status_code == 200:
    doc_id = response.json()['document_id']
    print("\n✅ hino_raw_logs No. 001 업로드 성공!")
    print(f"📄 문서 ID: {doc_id}")
    print(f"🔗 Firebase Console: https://console.firebase.google.com/project/jnext-e3dd9/firestore/databases/-default-/data/~2Fhino_raw_logs~2F{doc_id}")
