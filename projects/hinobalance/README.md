# HinoBalance (하이노밸런스)

JNext 프로젝트 Phase 1 - 하이노밸런스 운동 이론 및 실전 관리

## 프로젝트 구조

```
hinobalance/
├── data/                    # 원본 데이터
│   ├── theory/             # 카테고리별 이론 파일
│   ├── exercises/          # 개별 운동 설명
│   └── combined/           # 통합 이론 문서
│
├── scripts/                # HinoBalance 전용 스크립트
│   ├── analyze.py          # 분석 도구
│   ├── create.py           # 생성 도구
│   ├── publishing.py       # Draft→Final 출판 변환
│   ├── upload/             # Firestore 업로드 스크립트
│   └── organize/           # 데이터 정리 스크립트
│
└── docs/                   # 프로젝트 문서
    └── HINO_API_EXAMPLES.md
```

## 데이터 구조

Firestore Collection: `projects/hinobalance/{raw, draft, final}`

### 카테고리
- **이론**: 요약, 중간, 전체, 가치
- **실전**: 하이노워밍, 하이노골반, 하이노워킹, 하이노스케이팅, 하이노풋삽, 하이노철봉
- **밈**
- **숏**

## 주요 기능

### 1. 정밀분석 ("정밀분석해" 명령어)
7가지 항목으로 구조화된 분석 제공:
1. 분석 (내용)
2. 주요 효과
3. 추천 대상
4. 동작 요약
5. 종합 평점
6. 장점과 단점
7. 개선 및 발전 방향

### 2. 출판 시스템
- **Raw**: 원본 입력 데이터
- **Draft**: AI 초안 (자동 생성)
- **Final**: 출판용 최종본 (Draft 정제)

### 3. AI 모델 통합
- **젠 (Gemini)**: 정확한 분석
- **진 (GPT)**: 창의적 해석
- **클로 (Claude)**: 균형 잡힌 응답

## 관련 파일

### Django 앱 연동
- `api/api/projects/hinobalance.py` - 프로젝트 설정 클래스
- `api/api/ai_config.py` - AI 시스템 프롬프트

### 스크립트 위치
- HinoBalance 전용: `projects/hinobalance/scripts/`
- 범용 유틸리티: `api/scripts/`

## 개발 일정

현재 진행 상황은 `docs/작업일정.md` 참조
