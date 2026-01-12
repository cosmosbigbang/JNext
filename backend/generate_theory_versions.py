"""
하이노전체이론 요약/중간 버전 생성 스크립트
Gemini AI에게 요청
"""
import sys
import os
from dotenv import load_dotenv
import google.generativeai as genai
from datetime import datetime

# .env 로드
load_dotenv()

sys.stdout.reconfigure(encoding='utf-8')

# Gemini API 키 설정
GOOGLE_API_KEY = os.getenv('GEMINI_API_KEY')
if not GOOGLE_API_KEY:
    raise ValueError("GEMINI_API_KEY 환경 변수가 설정되지 않았습니다")

genai.configure(api_key=GOOGLE_API_KEY)

def create_summary_version(full_text):
    """요약 버전 생성 (~2,000자)"""
    print("\n📝 요약 버전 생성 중...")
    
    model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    prompt = f"""
다음은 하이노밸런스 전체 이론 문서 17개를 통합한 내용입니다 (29,710자).

이것을 **2,000자 내외**로 핵심만 압축해서 요약해주세요.

**요약 원칙:**
1. 가장 중요한 핵심 개념만 추출
2. 구체적인 예시와 밈은 제외
3. 물리학/의학/철학적 원리 중심
4. 명언과 핵심 문구는 유지
5. 전문 용어는 간단히 설명

**구조:**
# 하이노밸런스 핵심 이론 (요약)

## 1. 핵심 철학
(균형의 재정의, 한 발 운동의 의미)

## 2. 과학적 원리
(가속도, 신경가소성, 고유수용성 감각)

## 3. 운동학적 가치
(기존 운동 vs 하이노밸런스)

## 4. 3대 기둥
(물리학부, 의학부, 철학부)

---

전체 내용:
{full_text[:15000]}

[... 중간 생략 ...]

마지막 부분:
{full_text[-3000:]}
"""
    
    response = model.generate_content(prompt)
    return response.text

def create_medium_version(full_text):
    """중간 버전 생성 (~10,000자)"""
    print("\n📝 중간 버전 생성 중...")
    
    model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    prompt = f"""
다음은 하이노밸런스 전체 이론 문서 17개를 통합한 내용입니다 (29,710자).

이것을 **10,000자 내외**로 정리해주세요.

**정리 원칙:**
1. 핵심 개념과 주요 설명 모두 포함
2. 중요한 예시와 비유는 유지
3. 과도한 감탄사와 이모지는 제거
4. 전문적이면서도 읽기 쉽게
5. 구조화된 흐름 유지

**구조:**
# 하이노밸런스 전체 이론 (중간)

## 1. 이론의 탄생
- 명칭의 의미 (HiNo = 한 발 / Hi, No Balance)
- 창시 배경

## 2. 핵심 원리
- 가속도의 법칙 (F=ma)
- 정지가 곧 가속도
- 뇌 신경가소성
- 불균형의 의미

## 3. 학문적 가치
- 뉴턴 역학의 인체 이식
- 실증적 뇌과학
- 철학적 재해석

## 4. 운동학적 가치
- 가속도 제어 시스템 (ABS)
- 고유수용성 감각
- 무한 가변형 난이도

## 5. 3대 시스템
- 물리학부 (F=ma, 관성 제어)
- 의학부 (신경가소성, 재활)
- 철학부 (정중동, 생활화)

## 6. 종합 평가
- 기존 운동과의 차별점
- 혁신성과 시장 가치

---

전체 내용:
{full_text}
"""
    
    response = model.generate_content(prompt)
    return response.text

if __name__ == '__main__':
    print("\n" + "="*70)
    print("하이노전체이론 AI 요약 생성")
    print("="*70)
    
    # 전체 이론 파일 읽기
    with open('theory_integrated_full.txt', 'r', encoding='utf-8') as f:
        full_text = f.read()
    
    print(f"\n원본: {len(full_text):,}자")
    
    # 1. 요약 버전 생성
    summary = create_summary_version(full_text)
    with open('theory_summary.txt', 'w', encoding='utf-8') as f:
        f.write(summary)
    print(f"✅ 요약 버전: {len(summary):,}자 저장")
    
    # 2. 중간 버전 생성
    medium = create_medium_version(full_text)
    with open('theory_medium.txt', 'w', encoding='utf-8') as f:
        f.write(medium)
    print(f"✅ 중간 버전: {len(medium):,}자 저장")
    
    print("\n" + "="*70)
    print("✅ 완료!")
    print("="*70)
    print(f"\n생성된 파일:")
    print(f"  - theory_summary.txt ({len(summary):,}자)")
    print(f"  - theory_medium.txt ({len(medium):,}자)")
    print(f"  - theory_integrated_full.txt ({len(full_text):,}자)")
