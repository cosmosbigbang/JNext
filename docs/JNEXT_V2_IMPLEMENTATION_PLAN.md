# JNext v2 구현 계획서
작성일: 2026-01-14
작성자: J님 + Claude

---

## 🎯 핵심 목표
1. **슬라이더 2개 분리**: Temperature(창의성) + DB 사용률
2. **데이터 구조 재설계**: chat_history + project별 컬렉션 (raw/draft/final)
3. **자동 분석/정리**: AI를 활용한 3단계 저장 프로세스
4. **프로젝트 동적 생성**: 대화 중 신규 프로젝트 자동 생성
5. **AI 자기언급 제거**: 순수한 지식 데이터 확보

---

## 📊 데이터 구조 설계

### 1. chat_history (전체 대화 백업)
```firestore
{
  id: "20260114_093000_123456"
  역할: "user" | "assistant"
  원본_내용: "사용자가 말한 그대로"
  ai_응답: "AI 답변" (assistant인 경우)
  시간: timestamp
  모델: "gemini-pro"
  temperature: 0.85
  db_focus: 25
  project_context: "hinobalance" | null
  raw_분석_완료: false | true
  raw_저장_위치: "hinobalance_raw/xxx" (있으면)
}
```

### 2. {project}_raw (1차 정리 저장소)
```firestore
{
  id: "20260114_093000_123456"
  제목: "하이노워킹 크로스 개선안" (AI 생성)
  원본: "사용자 원본 메시지"
  ai_응답: "AI 답변 원본"
  정리본: "AI가 요약/정제한 내용"
  키워드: ["하이노워킹", "크로스", "골반"]
  카테고리: "하이노워킹" (운동별 분류)
  태그: ["개선", "아이디어", "피드백"]
  요약: "50자 핵심 요약"
  chat_ref: "20260114_093000_123456"
  project_id: "hinobalance"
  시간: timestamp
  작성자: "J님"
}
```

### 3. {project}_draft (가공 문서)
```firestore
{
  id: "20260114_100000_123456"
  제목: "하이노워킹 통합 이론 v1.0"
  내용: "정리된 긴 문서 (AI 언급 제거됨)"
  source_raws: ["raw_id1", "raw_id2", "raw_id3"]
  키워드: ["하이노워킹", "이론", "체계"]
  카테고리: "이론서"
  요약: "하이노워킹 전체 이론 통합..."
  버전: "1.0"
  project_id: "hinobalance"
  시간: timestamp
}
```

### 4. {project}_final (최종 출력물)
```firestore
{
  id: "20260114_110000_123456"
  제목: "하이노워킹 밈 - 크로스의 비밀"
  내용: "최종 밈 텍스트 (AI 언급 완전 제거)"
  출력_형식: "밈" | "전자책" | "숏폼"
  source_draft: "draft_id"
  키워드: ["밈", "크로스", "유머"]
  시간: timestamp
  파일_경로: "/meme_images/hino_cross_001.png"
}
```

### 5. projects_meta (프로젝트 메타 정보)
```firestore
{
  id: "jbody"
  display_name: "JBody"
  created_at: timestamp
  collections: ["jbody_raw", "jbody_theory", "jbody_draft", "jbody_final"]
  description: "몸 변화 추적 프로젝트"
  creator: "J님"
}
```

---

## 🔄 데이터 흐름 (3단계 프로세스)

### Stage 1: 대화 + 즉시 백업
```
사용자 메시지
  ↓
chat_history 저장 (원본 보존)
  ↓
AI 호출 (temperature, db_focus 적용)
  ↓
AI 응답 반환
  ↓
chat_history에 AI 응답 저장
```

### Stage 2: 가치 판단 (프로젝트만)
```
if project_id exists:
  ↓
AI 평가 호출 (temp 0.2, 저렴한 모델)
  ├─ Prompt: "명백한 잡담인가? 애매하면 무조건 yes"
  └─ 응답: yes (저장) | no (skip)
```

### Stage 3: RAW 분석 저장 (가치 있는 것만)
```
if 평가 = yes:
  ↓
AI 분석 호출 (temp 0.3)
  ├─ 제목 생성
  ├─ 키워드 추출
  ├─ 카테고리 분류
  └─ 요약 생성
  ↓
{project}_raw 저장
  ↓
chat_history 업데이트 (raw_분석_완료=true)
```

---

## 🎚️ 슬라이더 2개 설계

### 슬라이더 1: 창의성 (Temperature)
- 범위: 0-100 (UI) → 0.0-1.0 (실제값)
- 기본값: 85 (0.85)
- 대화/프로젝트 공통 적용
- 표시: "창의성: 0.85"

### 슬라이더 2: DB 사용률
- 범위: 0-100%
- 기본값: 대화 25%, 프로젝트 50%
- 프로젝트 전환 시 자동 조정
- 표시: "DB 사용: 50%"

### 가중치 계산
```python
conversation_weight = 15  # 고정
project_weight = int(15 + (db_focus * 0.7))
general_weight = 100 - 15 - project_weight
```

---

## 🆕 프로젝트 동적 생성

### 명령어 감지
- "JBody 프로젝트 만들어"
- "/프로젝트 JBody"
- AI가 대화 내용 분석 → 신규 프로젝트 의도 감지

### 생성 프로세스
```
1. projects_meta에 문서 생성
2. 4개 컬렉션 생성 (raw/theory/draft/final)
3. project_manager 동적 등록
4. UI 드롭다운 자동 반영 (/api/v2/projects)
```

---

## 🚫 AI 자기언급 제거

### DRAFT/FINAL 생성 시 프롬프트
```
절대 금지:
- AI 자기 언급 ("제가", "저는", "AI", "젠", "진", "클로")
- 분석 과정 언급 ("분석한 결과", "판단하건대")
- 추천/제안 표현 ("추천합니다", "제안드립니다")

원칙:
- RAW 데이터의 핵심만 추출하여 객관적으로 정리
- 마치 J님이 직접 작성한 것처럼
- 순수한 지식/이론/방법론만 담기
```

### 후처리 정규식
```python
patterns = [
    r"제가?\s*", r"저는\s*", r"AI(가|는|로서)?\s*",
    r"(젠|진|클로)(이|가|은|는)?\s*",
    r"분석한\s*결과,?\s*",
    r"추천(합니다|드립니다)", r"제안(합니다|드립니다)"
]
```

---

## 📱 UI 변경사항

### 웹 (chat_v2.html)
1. 슬라이더 1개 → 2개로 분리
2. 실시간 값 표시 추가
3. 프로젝트 드롭다운 동적 로딩 (/api/v2/projects)

### 모바일 (jnext_mobile)
1. 슬라이더 2개 추가
2. 프로젝트 목록 API 연동
3. 동일한 로직 적용

---

## 🔧 API 변경사항

### 새 엔드포인트
- `GET /api/v2/projects`: 프로젝트 목록 조회
- `POST /api/v2/projects`: 신규 프로젝트 생성

### 수정 엔드포인트
- `POST /api/v2/chat`: temperature, db_focus 파라미터 추가

---

## ⚠️ 주의사항

### 1차 필터링 원칙
- **관대하게**: 애매하면 무조건 저장
- False Negative (중요한 걸 버림) > False Positive (쓸데없는 걸 저장)
- 명백한 잡담만 제외: "안녕", "ㅋㅋㅋ", "고마워"

### Temperature 통제
- 대화: 0.85 (창의적)
- 평가: 0.2 (정확한 판단)
- 분석: 0.3 (정확한 추출)
- DRAFT 생성: 0.4-0.5 (구조화)

### 거짓말/환각 방지
- System Prompt에 명시
- "근거 없는 추측 절대 금지"
- "확실하지 않으면 명시"

---

## 📝 기존 데이터 마이그레이션

### 하이노밸런스 데이터 정리
1. 기존 컬렉션 백업
2. AI 언급 제거 스크립트 실행
3. 새 구조로 변환
4. 검증 후 배포

---

## 🎯 테스트 항목

### Phase 1: 슬라이더 테스트
- Temperature 변화에 따른 창의성 체감
- DB 사용률에 따른 맥락 변화
- 최적값 찾기 (J님 직접 테스트)

### Phase 2: 저장 프로세스 테스트
- chat_history 저장 확인
- 가치 평가 정확도
- RAW 분석 품질

### Phase 3: 프로젝트 생성 테스트
- 명령어 감지
- 컬렉션 생성
- UI 반영

### Phase 4: AI 언급 제거 테스트
- DRAFT/FINAL 생성 시 검증
- 기존 데이터 정리 확인

---

## 🚀 다음 단계
J님 확인 후 순서도 보고 작업 시작!
