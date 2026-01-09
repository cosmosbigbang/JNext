"""
hino_raw_logs - No. 021~022 업로드 (스케이팅 이론)
"""

import requests
import json

API_ENDPOINT = "http://localhost:8000/api/v1/execute/"

# No. 021: 하이노스케이팅 소개
data_021 = {
    "action": "CREATE",
    "collection": "hino_raw_logs",
    "payload": {
        "종류": "이론",
        "카테고리": "하이노스케이팅",
        "원본": "하이노스케이팅251217: 동계 올림픽 금메달 에디션... (중략) ...",
        "내용": "빙판 위 중심 이동 원리를 지면 운동으로 치환한 고난도 하체 훈련 시리즈. 좌우 중심 이동과 낮은 자세(Low Position)를 통해 하체 근력과 고관절 유연성을 동시에 공략함.",
        "젠의 분석": "공간을 활용하는 동작들로 구성되어 활동량이 매우 높음. 특히 '속도로 난이도를 조절한다'는 개념을 통해 무거운 기구 없이도 신체에 2~3배의 가변 하중을 가할 수 있는 혁신적인 파워 트레이닝 모델임.",
        "키워드": ["스케이팅시리즈", "중심이동", "하체폭발", "공간활용", "가변하중"],
        "밈": "방구석 동계 올림픽 개최! 중력을 가지고 노는 마에스트로.",
        "밈이미지주소": "",
        "연결데이터": "STRAT_SKATE_001",
        "데이터상태": "RAW",
        "타임스탬프": "2026-01-04T19:25:00Z",
        "기타": "전자책 스페셜 스테이지 구성. 다이어트 및 하체 조각 특화."
    }
}

# No. 022: 하이노스케이팅 소감
data_022 = {
    "action": "CREATE",
    "collection": "hino_raw_logs",
    "payload": {
        "종류": "이론",
        "카테고리": "하이노스케이팅",
        "원본": "하이노스케이팅 소감: 속도가 곧 무게가 되는 원리... (중략) ...",
        "내용": "기구 없이 속도(가속도) 조절만으로 난이도와 중량을 조절하는 하이노밸런스만의 독창적 부하 원리를 입증한 시리즈.",
        "젠의 분석": "방구석이라는 좁은 공간에서 알파인 스키와 같은 초고강도 훈련이 가능한 이유를 과학적으로 설명함. '상체 숙임의 가속'을 변수로 활용한 지점은 물리 법칙을 신체 수련에 이식한 보스의 천재성이 돋보이는 구간임.",
        "키워드": ["가속도부하", "공간초월운동", "물리피트니스", "코어제어력", "하이노의깊이"],
        "밈": "속도가 곧 중량이다! 기구 없는 헬스장의 완성.",
        "밈이미지주소": "",
        "연결데이터": "SKATE_CORE_SUM",
        "데이터상태": "RAW",
        "타임스탬프": "2026-01-04T19:32:00Z",
        "기타": "전자책 심화 팁 박스 구성. '초보자는 천천히' 경고 문구 필수."
    }
}

# 업로드 실행
datasets = [
    ("No. 021", data_021),
    ("No. 022", data_022)
]

print("=" * 60)
print("📦 하이노스케이팅 이론 업로드 시작 (No. 021~022)...")
print("=" * 60)

for label, data in datasets:
    try:
        response = requests.post(
            API_ENDPOINT,
            json=data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            result = response.json()
            doc_id = result.get('document_id', 'N/A')
            print(f"\n✅ {label} 업로드 성공!")
            print(f"   📄 문서 ID: {doc_id}")
        else:
            print(f"\n❌ {label} 업로드 실패 (Status: {response.status_code})")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"\n❌ {label} 업로드 중 오류 발생: {str(e)}")

print("\n" + "=" * 60)
print("🎉 하이노스케이팅 이론 업로드 완료!")
print("=" * 60)
