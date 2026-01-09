"""
Gemini Chat API 테스트
"""
import json
import urllib.request

url = "http://127.0.0.1:8000/api/v1/chat/"
data = {
    "message": "안녕하세요, JNext 테스트입니다. Firestore에 있는 데이터를 조회해주세요.",
    "mode": "organize"
}

req = urllib.request.Request(
    url,
    data=json.dumps(data).encode('utf-8'),
    headers={'Content-Type': 'application/json'}
)

try:
    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read().decode('utf-8'))
        print(json.dumps(result, indent=2, ensure_ascii=False))
except Exception as e:
    print(f"Error: {e}")
