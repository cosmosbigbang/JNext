"""
Gemini 사용 가능한 모델 목록 확인
"""
import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))

print("=== 사용 가능한 Gemini 모델 목록 ===\n")

try:
    models = client.models.list()
    for model in models:
        print(f"- {model.name}")
        if hasattr(model, 'display_name'):
            print(f"  Display: {model.display_name}")
        if hasattr(model, 'supported_generation_methods'):
            print(f"  Methods: {model.supported_generation_methods}")
        print()
except Exception as e:
    print(f"Error: {e}")
