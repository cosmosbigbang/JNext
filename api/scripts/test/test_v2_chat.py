"""
Chat API v2 테스트 스크립트
"""
import json
import urllib.request
import sys

# --- 테스트 설정 ---
BASE_URL = "http://127.0.0.1:8000/api/v2/chat/"
USER_ID = "test_user_01"
PROJECT_ID = "hinobalance"

# --- 테스트 시나리오 ---

# 시나리오 1: 일반 대화 (GENERAL_SYSTEM_PROMPT 사용 기대)
scenario_1_data = {
    "user_id": USER_ID,
    "project_id": PROJECT_ID,
    "message": "하이노밸런스라는 운동에 대해 간단히 소개해줄래? 너의 생각은?",
    "db_focus": 0 
}

# 시나리오 2: 정밀 분석 요청 (HINOBALANCE_SYSTEM_PROMPT 사용 기대)
scenario_2_data = {
    "user_id": USER_ID,
    "project_id": PROJECT_ID,
    "message": """
다음은 하이노워밍기본 내용이야.. 정밀분석해줘

하나로 중심 잡고 다리를 번갈아 들면서 ... 다리를 내릴때.. 몸을 나추며 체중을 일부를 실음..
몸이 더 풀릴수록 체중을 중심발에 더 실음... 다리를 바꾸는 자세는 춤을 추듯이.. 리듬감 있게함
몸이 풀리면 다리를 앞으로 쭉뻗으며 중심발을 나추며 체중을 실으며.. 역시 춤듯이 리듬감 있게 발을 바꿈..
몸이 풀리면 다리를 앞으로 벋고 회수할때 발바꾸지 말고 그대로 뒤로 죽뻗음.. 시선은 전방주시..
한다리 3~5번하며 발바꾸고 ... 리듬감있게 하며 중심발은 상하 움직이며 함..
몸이 풀리면 전방 고점, 후방고점 에서 정지자세 추가함.. 발바꿔 하며 3세트 하고 ..
이번에는 발을 앞으로 쭉벋은 자세 극대로 쭉 위로 올림.. 오금에 자극이 제대로 와야함.
한다리당 3~5번하고 발바꿔도 돼곡 한번씩 번갈아 해도됨..
하이노밸런스 몸풀때 제일 먼저 하는 운동
""",
    "db_focus": 0
}

def run_test(scenario_name, data):
    """지정된 시나리오로 API 테스트를 실행"""
    print(f"--- Running Test: {scenario_name} ---")
    
    req = urllib.request.Request(
        BASE_URL,
        data=json.dumps(data).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )

    try:
        with urllib.request.urlopen(req) as response:
            if response.status == 200:
                result = json.loads(response.read().decode('utf-8'))
                print(json.dumps(result, indent=2, ensure_ascii=False))
                print(f"--- Test Succeeded: {scenario_name} ---\n")
                return True
            else:
                print(f"Error: Received status code {response.status}")
                print(response.read().decode('utf-8'))
                print(f"--- Test Failed: {scenario_name} ---\n")
                return False

    except Exception as e:
        print(f"An exception occurred: {e}")
        print(f"--- Test Failed: {scenario_name} ---\n")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        test_to_run = sys.argv[1]
        if test_to_run == '1':
            run_test("Scenario 1: General Conversation", scenario_1_data)
        elif test_to_run == '2':
            run_test("Scenario 2: Detailed Analysis", scenario_2_data)
        else:
            print("Invalid argument. Use '1' for Scenario 1 or '2' for Scenario 2.")
    else:
        print("Running all scenarios...")
        run_test("Scenario 1: General Conversation", scenario_1_data)
        run_test("Scenario 2: Detailed Analysis", scenario_2_data)
