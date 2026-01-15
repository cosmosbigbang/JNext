# Session Summary 구조 설계

## 개요
진·젠이 공동 추천한 "대화 3줄 요약" 기능
- 목적: 대화 100개 → 10개 + 요약 3줄로 압축, 노이즈 제거
- 효과: 모바일 AI처럼 순수한 맥락 유지, 토큰 효율 극대화

## 핵심 설계

### 1. 요약 시점
- **10개 대화마다 자동 요약** (백그라운드)
- 사용자 인지 없이 자동 실행
- 실시간 요약 X, 비동기 처리 O

### 2. 요약 내용 (3줄)
```
1. [문제] J님이 무엇을 해결하려고 했는지
2. [과정] 어떤 시도와 결과가 있었는지
3. [결론] 최종 해결 방법 또는 현재 상태
```

### 3. 저장 위치
- **Firestore**: `chat_summaries` 컬렉션
- 구조:
```
chat_summaries/
  {timestamp_id}/
    - created_at: datetime
    - chat_range: [100, 110]  # 어떤 대화들을 요약했는지
    - summary: "1. [문제]... 2. [과정]... 3. [결론]..."
    - project: "hinobalance" or null
```

### 4. 맥락 구성 변경
**현재 (문제)**
```python
conversation_history = load_chat_history(limit=100)
```

**개선 (솔루션)**
```python
# 1. 최근 대화 10개
recent_chats = load_chat_history(limit=10)

# 2. 요약 3개 (30개 대화 압축)
summaries = load_chat_summaries(limit=3)

# 3. 맥락 구성
context = f"""
[과거 대화 요약]
{summaries}

[최근 대화]
{recent_chats}
"""
```

## 구현 우선순위

### Phase 1 (즉시 실행 완료)
- ✅ System Prompt 축소 (2000 → 500자)
- ✅ DB 기본 10%로 변경
- ✅ RAW→DRAFT 정리 시 DB 100% + Pro

### Phase 2 (다음 단계)
1. `chat_summaries` 컬렉션 생성
2. `create_chat_summary()` 함수 구현
   - AI 호출: "최근 10개 대화를 3줄로 요약"
   - Firestore 저장
3. `load_chat_summaries()` 함수 구현
4. `chat_v2()` 함수 수정
   - `conversation_history` → `recent_chats (10개) + summaries (3개)`

### Phase 3 (자동화)
1. 백그라운드 작업: 10개 대화마다 요약 생성
2. 오래된 요약 정리 (30일 이상)

## 예상 효과

### 현재 문제
- 대화 100개 = 평균 50,000 토큰
- 노이즈 많음 (잡담, 반복, 오류)
- AI가 "최근" vs "오래된" 구분 못함

### 개선 후
- 대화 10개 + 요약 3줄 = 평균 5,000 토큰 (90% 감소)
- 핵심만 전달 (문제-과정-결론)
- AI가 "전체 흐름" 이해 + "최근 맥락" 집중

## 진·젠 진단 핵심

### 진의 진단
- **우선순위**: 1위=최근대화 10개, 2위=요약 3줄, 3위=Prompt, 4위=DB
- **효과**: "경쟁 상태" 해소, 명확한 우선순위

### 젠의 진단
- **효과**: "프롬프트 희석" 방지, 맥락 과부하 해소
- **토큰**: 100개 → 10개+요약으로 90% 절감

## 코드 위치 (구현 시 참고)

### 파일들
- `api/views_v2.py`: chat_v2() 함수 (라인 50-200)
- `api/views.py`: load_chat_history() 함수
- **신규**: `api/summary_manager.py` (생성 필요)

### 함수들
```python
# summary_manager.py
def create_chat_summary(chats: list) -> str
def load_chat_summaries(limit: int) -> str
def should_create_summary() -> bool  # 10개마다 True
```

## 참고사항
- 모바일 AI가 우수한 이유: 순수 대화 맥락 1000개 (DB 참조 없음)
- JNext 목표: 대화 맥락 최소화 + DB 참조 최소화 → 모바일 수준 달성
