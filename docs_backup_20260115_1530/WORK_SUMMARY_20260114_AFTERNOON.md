# JNext v2 완료 작업 정리 (2026-01-14)

## ✅ 완료된 주요 작업

### 1. 듀얼 슬라이더 시스템 (Phase 1)
**파일**: `chat_v2.html`, `views_v2.py`, `context_manager.py`

**기능**:
- **Temperature 슬라이더**: 0-100 (UI) → 0.0-1.0 (실제값)
  - 대화 모드 기본값: 85 (0.85, 창의적)
  - 프로젝트 모드 기본값: 85 유지
  - AI 평가: 0.2 (정확한 판단)
  - AI 분석: 0.3 (정밀한 추출)

- **DB Focus 슬라이더**: 0-100%
  - 대화 모드 기본값: 25%
  - 프로젝트 모드 기본값: 50% (자동 전환)
  - 가중치 계산:
    * 대화 맥락: 15% (고정)
    * 프로젝트 DB: 15 + (db_focus × 0.7) = 15-85%
    * 일반 지식: 나머지

**구현 상세**:
```javascript
// chat_v2.html
- Temperature: #temp-slider, #temp-value (85 → 0.85)
- DB Focus: #db-slider, #db-value (25% / 50%)
- Auto-adjust: projectSelect onChange → DB 25%↔50%
```

---

### 2. chat_history 스키마 확장 (Phase 2)
**파일**: `views.py` - `save_chat_history()`

**추가 필드** (5개):
- `temperature`: float (0.0-1.0)
- `db_focus`: int (0-100)
- `project_context`: str (프로젝트 ID 또는 None)
- `raw_분석_완료`: bool (RAW 저장 여부)
- `raw_저장_위치`: str (RAW doc_id 참조)

**기능**:
- 모든 대화 백업 (전역 chat_history)
- RAW 저장 시 cross-reference 생성
- 슬라이더 값 히스토리 추적

---

### 3. 3-Stage Storage 프로세스 (Phase 3)
**파일**: `raw_storage.py` (신규), `views_v2.py`

**워크플로우**:
```
사용자 메시지 → AI 응답
    ↓
chat_history 저장 (백업) ← temperature, db_focus 포함
    ↓
[프로젝트 모드인가?] → Yes
    ↓
evaluate_chat_value() - AI 평가 (temp 0.2)
    ↓
[저장 가치 있는가?] → Yes (애매하면 yes)
    ↓
analyze_and_save_raw() - AI 분석 (temp 0.3)
    ↓
projects/{project_id}/raw/{timestamp} 저장
    ↓
chat_history 업데이트 (raw_분석_완료=True, raw_저장_위치=doc_id)
```

**AI 평가 기준** (lenient):
- 명백한 인사/감탄사만 no
- 질문, 아이디어, 의견, 피드백 등 모두 yes
- **애매하면 무조건 yes** (중요 내용 놓치면 안 됨)

**RAW 문서 스키마**:
```python
{
    'id': 'YYYYMMDD_HHMMSS_microseconds',
    '제목': AI 추출 (15자 이내),
    '원본': 사용자 원본 메시지,
    'ai_응답': AI 응답 전체,
    '정리본': AI 응답 (나중에 정제),
    '키워드': AI 추출 리스트,
    '카테고리': AI 분류 (하이노워킹, 하이노골반 등),
    '태그': [],
    '요약': AI 요약 (1문장),
    'chat_ref': chat_history doc_id,
    'project_id': 'hinobalance',
    '시간': timestamp,
    '작성자': 'J님',
    '모델': 'gemini-pro/flash'
}
```

---

### 4. AI 자기언급 제거 시스템
**파일**: `raw_storage.py`

**2단계 방어**:

**1차: 프롬프트 강화**
```python
**절대 규칙:**
1. AI 자기언급 완전 제거: "제가", "저는", "AI", "젠", "진", "클로", "어시스턴트" 등 모든 표현 삭제
2. 객관적 사실과 핵심 내용만 포함 (3인칭 시점)
3. 근거 없는 추측 금지
4. 확실하지 않으면 "불명확" 명시
```

**2차: Regex 후처리**
```python
import re
ai_self_refs = r'(제가|저는|저희는|젠|젠시|진|클로|AI|어시스턴트|assistant|I am|I\'m|As an AI)'
for key in ['제목', '요약']:
    if key in metadata:
        metadata[key] = re.sub(ai_self_refs, '', metadata[key], flags=re.IGNORECASE)
        metadata[key] = re.sub(r'\s+', ' ', metadata[key]).strip()
```

---

### 5. Firestore Hierarchical 구조 마이그레이션
**파일**: `migrate_firestore.py` (신규)

**Before (Flat)**:
```
hino_raw/{doc_id}
hino_draft/{doc_id}
hino_final/{doc_id}
hino_theory/{doc_id}
```

**After (Hierarchical)**:
```
projects/
  hinobalance/
    (metadata document)
    raw/{doc_id}
    draft/{doc_id}
    final/{doc_id}
    theory/{doc_id}
```

**마이그레이션 결과**:
- ✅ 70개 문서 이동 (raw: 39, draft: 31, final: 0, theory: 0)
- ✅ projects/hinobalance 메타데이터 생성
- ⚠️ 구형 컬렉션 (hino_*) 보존 (롤백 대비)

---

### 6. 전체 코드베이스 업데이트 (Hierarchical)
**수정된 파일** (10개):

1. **chat_v2.html**: 프로젝트 select value "hino" → "hinobalance"
2. **views_v2.py**: temperature/db_focus 파라미터, RAW 저장 로직
3. **context_manager.py**: 듀얼 슬라이더 독립 제어
4. **views.py**: save_chat_history() 확장, hino_review_draft() 경로 수정
5. **raw_storage.py**: 평가/분석/저장 전체 로직 (신규)
6. **hinobalance.py**: project_id "hinobalance", 모든 쿼리 hierarchical
7. **project_manager.py**: get_default_project() "hinobalance"
8. **ai_service.py**: 컬렉션 이름 "draft"/"final"/"raw" (서브컬렉션)
9. **automation.py**: 모든 쿼리 projects/hinobalance/* 경로
10. **settings.py**: COLLECTION_RAW/DRAFT/FINAL → "raw"/"draft"/"final"
11. **base.py**: get_collection_name() 서브컬렉션 이름만 반환

---

### 7. 테스트 스크립트 작성
**파일**: `test_v2_complete.py` (신규)

**테스트 항목** (6개):
1. 듀얼 슬라이더 파라미터 전송 확인
2. 3-Stage Storage (RAW 저장) 검증
3. Hierarchical Firestore 쿼리 테스트
4. AI 자기언급 제거 확인
5. ProjectManager 프로젝트 로딩
6. chat_history 확장 스키마 확인

**실행 방법**:
```powershell
cd backend
.\venv\Scripts\Activate.ps1
python test_v2_complete.py
```

---

## 🔧 시스템 구성

### Firestore 구조
```
chat_history/                    # 전역 대화 백업
  {timestamp}/
    역할: "user" | "assistant"
    내용: str
    시간: timestamp
    모드: "conversation" | "project"
    모델: "gemini-pro" | "gemini-flash" | "gpt-4o" | "claude"
    temperature: float (0.0-1.0)
    db_focus: int (0-100)
    project_context: str | None
    raw_분석_완료: bool
    raw_저장_위치: str | None

projects/
  hinobalance/                   # 프로젝트 메타데이터
    display_name: "하이노밸런스"
    created_at: timestamp
    collections: ["raw", "draft", "final", "theory"]
    
    raw/{timestamp}/             # 원본 아이디어
      제목, 원본, ai_응답, 정리본, 키워드, 카테고리, 태그, 요약
      chat_ref, project_id, 시간, 작성자, 모델
    
    draft/{doc_id}/              # 정리 중
      exercise_name, title, content, category, content_type
    
    final/{doc_id}/              # 최종 배포
      전체글, 카테고리, 제목, 난이도, 밈
    
    theory/{doc_id}/             # 이론 통합
```

### Temperature 전략
| 단계 | Temperature | 용도 |
|------|------------|------|
| 대화 (기본) | 0.85 | 창의적 대화, RAW 생성 |
| 평가 | 0.2 | 정확한 가치 판단 |
| 분석 | 0.3 | 정밀한 메타데이터 추출 |
| DRAFT 생성 | 0.4-0.5 | 체계적 정리 |
| FINAL 생성 | 가변 | 콘텐츠 유형별 조정 |

### DB Focus 가중치
| Focus | 대화 | 프로젝트 DB | 일반 지식 |
|-------|------|------------|----------|
| 0% | 15% | 15% | 70% |
| 25% (대화) | 15% | 32.5% | 52.5% |
| 50% (프로젝트) | 15% | 50% | 35% |
| 100% | 15% | 85% | 0% |

---

## 📊 통계

### 코드 변경
- **수정된 파일**: 11개 (신규 3개 포함)
- **추가된 코드**: ~500줄
- **삭제/수정된 코드**: ~200줄
- **테스트 코드**: 280줄

### 데이터 마이그레이션
- **이동된 문서**: 70개
- **RAW**: 39개
- **DRAFT**: 31개
- **FINAL**: 0개
- **THEORY**: 0개

---

## 🚀 다음 단계 (J님 오후 작업)

### 우선순위 P0 (필수)
1. **서버 재시작**
   ```powershell
   cd backend
   .\venv\Scripts\Activate.ps1
   python manage.py runserver
   ```

2. **웹 UI 테스트** (`http://localhost:8000/chat/v2/`)
   - [ ] 듀얼 슬라이더 표시 확인
   - [ ] Temperature 슬라이더 85 기본값
   - [ ] DB 슬라이더 25% 기본값
   - [ ] 프로젝트 선택 시 DB 50% 자동 전환
   - [ ] 채팅 기능 정상 작동

3. **자동 테스트 실행**
   ```powershell
   python test_v2_complete.py
   ```
   - 6개 테스트 모두 통과 확인

4. **RAW 저장 검증**
   - Firestore Console: `projects/hinobalance/raw` 확인
   - AI 자기언급 제거 확인

5. **구형 컬렉션 삭제**
   ```powershell
   python migrate_firestore.py
   # 옵션 2 선택 (old collections 삭제)
   ```

### 우선순위 P1 (선택)
- [ ] theory 서브컬렉션 삭제 (빈 컬렉션)
- [ ] Mobile app 테스트 (Flutter)
- [ ] Render 배포 확인

### 우선순위 P2 (나중에)
- [ ] Phase 4: 동적 프로젝트 생성 UI
- [ ] Phase 5: DRAFT→FINAL 자동화
- [ ] Phase 6: 밈 생성 파이프라인
- [ ] Phase 7: 성능 최적화

---

## 🐛 알려진 이슈

1. **Lint 경고**: `firebase_admin` import 경고 (실행에는 문제없음, venv 내 설치됨)
2. **구형 컬렉션**: hino_* 컬렉션 아직 존재 (테스트 후 삭제 예정)
3. **theory 서브컬렉션**: 빈 컬렉션 (수동 삭제 필요)

---

## 📝 설정 파일 요약

### settings.py
```python
COLLECTION_RAW = "raw"      # projects/{project_id}/raw
COLLECTION_DRAFT = "draft"  # projects/{project_id}/draft
COLLECTION_FINAL = "final"  # projects/{project_id}/final
```

### chat_v2.html
```html
<select id="project-select">
  <option value="">💬 대화</option>
  <option value="hinobalance">🏃 하이노밸런스</option>
</select>

<input type="range" id="temp-slider" min="0" max="100" value="85">
<input type="range" id="db-slider" min="0" max="100" value="25">
```

### project_manager.py
```python
def get_default_project():
    return 'hinobalance'
```

---

## 💡 핵심 개선사항

1. **독립적 슬라이더**: Temperature와 DB Focus 분리 → 세밀한 제어
2. **계층적 구조**: Multi-project 확장 가능한 Firestore 설계
3. **자동 RAW 저장**: 프로젝트 대화 자동 분류 및 저장
4. **AI 자기언급 제거**: 지식 베이스 품질 향상
5. **완전한 백업**: chat_history에 모든 대화 보존
6. **확장 가능성**: 새 프로젝트 추가 시 projects/{new_project} 생성만 하면 됨

---

**작성**: Claude (Copilot Agent)  
**날짜**: 2026-01-14  
**버전**: JNext v2.0  
**테스트 상태**: 미검증 (J님 오후 테스트 예정)
