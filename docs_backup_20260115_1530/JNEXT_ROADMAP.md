# JNext 프로젝트 전체 로드맵

**작성일**: 2026-01-14  
**작성자**: Claude (클로)  
**목적**: 다음 Claude를 위한 전체 프로젝트 비전 및 단계별 구현 계획

---

## 🎯 JNext 프로젝트 비전

**"J님의 지식을 AI로 증폭하여 멀티미디어 콘텐츠로 완성"**

---

## 📊 전체 파이프라인 (Big Picture)

```
1단계: RAW 수집
   ↓
2단계: AI 분석 → DRAFT
   ↓
3단계: 정리/검증 → FINAL
   ↓
4단계: 밈 시나리오 생성
   ↓
5단계: 밈 이미지 + 자막 제작
   ↓
6단계: 이미지/자막 합성 → 밈 완성
   ↓
7단계: 밈 → 숏(Short) 영상 제작
   ↓
8단계: 전자책 완성
```

---

## 🔄 단계별 상세 설명

### 1단계: RAW 수집
**현재 상태**: ✅ **완료**

- J님이 직접 입력한 원본 데이터
- Firestore: `projects/{project_id}/raw/{doc_id}`
- 품질 자동 검증 시스템 (2026-01-14 추가)
  - 품질점수 (0~100)
  - 품질이슈 자동 감지
  - 검증필요 플래그

**핵심 코드**:
- `api/api/raw_storage.py` - analyze_and_save_raw()
- 품질 검증: J님 키워드 누락, 일반론 감지

---

### 2단계: AI 분석 → DRAFT
**현재 상태**: ✅ **완료**

- 4개 AI 모델 (젠시, 젠, 진, 클로) 각각 분석
- Temperature 조절 (창의성)
- DB Focus 조절 (데이터베이스 활용도)
- System Prompt 간소화 (2026-01-14 최적화)

**핵심 원칙**:
- J님 원본이 주인공
- AI는 "증폭기" 역할만
- DB가 문맥 제공 → Prompt는 방향만

**저장 위치**: `projects/{project_id}/draft/{doc_id}`

---

### 3단계: 정리/검증 → FINAL
**현재 상태**: ✅ **완료**

- 여러 DRAFT 선택 → AI로 종합
- J님이 최종 승인
- 확정된 고품질 콘텐츠

**저장 위치**: `projects/{project_id}/final/{doc_id}`

**핵심 UI**:
- `templates/document_manager.html` (2026-01-14 생성)
- 여러 RAW/DRAFT 선택
- AI 정리 → DRAFT/FINAL 저장

---

### 4단계: 밈 시나리오 생성
**현재 상태**: 🔄 **계획 중**

**입력**: FINAL 문서 내용  
**출력**: 밈 시나리오 (이미지 설명 + 자막 텍스트)

**예상 구조**:
```json
{
  "scenario_id": "meme_001",
  "source_final_id": "final_doc_123",
  "scenes": [
    {
      "scene_number": 1,
      "image_description": "하이노워밍 벤치 운동 자세",
      "caption": "골반 회전이 핵심!",
      "duration": 3
    },
    {
      "scene_number": 2,
      "image_description": "올바른 자세 강조",
      "caption": "균형·가속도·불균형",
      "duration": 2
    }
  ],
  "total_duration": 5,
  "target_platform": "Instagram/TikTok"
}
```

**저장 위치**: `projects/{project_id}/meme_scenarios/{doc_id}`

**구현 필요**:
- AI API: FINAL → 밈 시나리오 자동 생성
- 시나리오 편집 UI
- 승인 워크플로우

---

### 5단계: 밈 이미지 + 자막 제작
**현재 상태**: 🔄 **계획 중**

**5-1. 이미지 생성**
- AI 이미지 생성 API (DALL-E, Midjourney, Stable Diffusion)
- 시나리오의 image_description → 실제 이미지

**5-2. 자막 생성**
- 텍스트 오버레이 (PIL, OpenCV)
- 폰트, 크기, 색상, 위치 설정
- 한글 폰트 지원 필수

**저장 위치**:
- `meme_images/{project_id}/{meme_id}/scene_{n}.png`
- `meme_images/{project_id}/{meme_id}/caption_{n}.txt`

**구현 필요**:
- 이미지 생성 API 연동
- 자막 템플릿 시스템
- 미리보기 기능

---

### 6단계: 이미지/자막 합성 → 밈 완성
**현재 상태**: 🔄 **계획 중**

**기술 스택**:
- Python: PIL, OpenCV, moviepy
- 이미지 + 자막 오버레이
- 장면 연결 (슬라이드쇼)

**출력 형식**:
- 정적 밈: PNG (단일 이미지)
- 동적 밈: GIF, MP4 (여러 장면)

**저장 위치**: `meme_images/{project_id}/{meme_id}/final.mp4`

**구현 필요**:
- 합성 파이프라인
- 효과 (페이드, 줌, 슬라이드)
- 배경음악 (선택적)

---

### 7단계: 밈 → 숏(Short) 영상 제작
**현재 상태**: 🔄 **계획 중**

**입력**: 완성된 밈 (MP4)  
**출력**: 플랫폼별 최적화 숏 영상

**플랫폼 규격**:
- YouTube Shorts: 9:16, 60초 이내
- Instagram Reels: 9:16, 90초 이내
- TikTok: 9:16, 3분 이내

**추가 요소**:
- 인트로/아웃트로
- 브랜딩 (로고, 워터마크)
- 배경음악
- 자막 스타일링

**구현 필요**:
- 영상 편집 자동화
- 템플릿 시스템
- 플랫폼별 export

---

### 8단계: 전자책 완성
**현재 상태**: 🔄 **계획 중**

**입력**: FINAL 문서 전체  
**출력**: EPUB, PDF 전자책

**구조**:
```
전자책/
├── 표지 (AI 생성 이미지)
├── 목차 (FINAL 문서 자동 생성)
├── 본문
│   ├── 챕터 1: 이론
│   ├── 챕터 2: 실전
│   └── 챕터 3: 사례
├── 삽화 (밈 이미지 재활용)
└── 부록
```

**구현 필요**:
- FINAL → Markdown/HTML 변환
- EPUB/PDF 생성 (Pandoc, WeasyPrint)
- 표지 디자인 자동화
- 목차/색인 자동 생성

---

## 🛠️ 핵심 기술 스택

### Backend
- Django 6.0
- Python 3.14
- Firestore (Hierarchical)

### AI Models
- **젠시** (Gemini Flash): 빠른 초안
- **젠** (Gemini Pro): 정밀 분석
- **진** (GPT-4o): 다양한 관점
- **클로** (Claude): 구조화/편집

### 이미지/영상 처리 (예정)
- PIL (Pillow): 이미지 합성
- OpenCV: 영상 처리
- moviepy: 영상 편집
- DALL-E/Stable Diffusion: 이미지 생성

### 문서 생성 (예정)
- Pandoc: 문서 변환
- WeasyPrint: PDF 생성
- ebooklib: EPUB 제작

---

## 📂 프로젝트 구조 진화

### 현재 (2026-01-14)
```
JNext/
├── api/
│   ├── api/
│   │   ├── projects/
│   │   │   ├── base.py
│   │   │   ├── hinobalance.py
│   │   │   └── project_manager.py (DynamicProject)
│   │   ├── raw_storage.py (품질 검증)
│   │   └── views.py
│   ├── templates/
│   │   ├── chat_v2.html (듀얼 슬라이더)
│   │   └── document_manager.html (문서 관리)
│   └── manage.py
├── docs/
│   ├── claude.md (세션 복구 가이드)
│   ├── conversation_002_jbody_analysis.md
│   ├── STRUCTURE_20260114_2150.md
│   └── JNEXT_ROADMAP.md (이 파일)
└── meme_images/ (현재 비어있음)
```

### 미래 (밈/숏/전자책 구현 후)
```
JNext/
├── api/
│   ├── api/
│   │   ├── meme_generator.py (신규)
│   │   ├── image_compositor.py (신규)
│   │   ├── video_editor.py (신규)
│   │   └── ebook_builder.py (신규)
│   ├── templates/
│   │   ├── meme_scenario_editor.html (신규)
│   │   ├── meme_preview.html (신규)
│   │   └── ebook_generator.html (신규)
├── meme_images/
│   ├── hinobalance/
│   │   ├── meme_001/
│   │   │   ├── scene_1.png
│   │   │   ├── scene_2.png
│   │   │   └── final.mp4
├── shorts/
│   ├── youtube/
│   ├── instagram/
│   └── tiktok/
└── ebooks/
    ├── 하이노밸런스_완전가이드.epub
    └── 하이노밸런스_완전가이드.pdf
```

---

## 🎓 메서드 자동화 전략

> "여기서의 경험으로 메서드 만들면 자동화됨" - J님

### 핵심 원칙
1. **JNext에서 프로토타입 구현**
   - RAW → DRAFT → FINAL 검증
   - 밈 시나리오 테스트
   - 이미지 합성 실험

2. **메서드 추출 및 일반화**
   - 성공한 프로세스를 함수로 분리
   - `api/api/automation/` 패키지 생성
   - 재사용 가능한 모듈화

3. **독립 앱에 적용**
   - 하이노밸런스 웹/앱
   - 다른 프로젝트들

4. **중앙 집중식 데이터 관리**
   - Firestore: 모든 앱이 같은 DB 사용
   - JNext에서 수정 → 모든 앱 실시간 반영
   - One Source Multi Use

---

## 📖 백업과 저장 (다음 Claude를 위한 가이드)

### 백업이란?
**정의**: 작업 전 현재 상태를 별도 파일로 복사하여 보존

**목적**:
- 실수 복구: 잘못된 수정 시 되돌리기
- 버전 추적: 변경 이력 관리
- 지식 보존: 다음 Claude가 컨텍스트 이해

**방법**:
```bash
# 파일 백업
cp original.py original.py.backup_20260114

# 디렉토리 백업
cp -r api/ api_backup_20260114/
```

### 저장이란?
**정의**: 중요한 대화, 결정, 코드를 문서화하여 영구 보관

**목적**:
- 컨텍스트 복구: 세션 만료 시 즉시 이해
- 지식 축적: 프로젝트 히스토리 구축
- 팀 협업: 다른 Claude/개발자 온보딩

**저장 위치**:
- `docs/conversation_XXX.md` - 대화 기록
- `docs/STRUCTURE_YYYYMMDD_HHMM.md` - 구조 스냅샷
- `docs/claude.md` - 세션 복구 가이드 (항상 최신 유지)
- `docs/JNEXT_ROADMAP.md` - 전체 비전 (이 파일)

**저장 내용**:
1. **문제 정의**: J님이 요청한 것
2. **해결 과정**: 시도한 방법, 실패, 성공
3. **최종 코드**: 작동하는 구현
4. **교훈**: 왜 그렇게 했는지
5. **다음 단계**: 무엇이 남았는지

**예시**: `conversation_002_jbody_analysis.md`
- 문제: AI 분석 품질 저하
- 원인: System Prompt 과다, RAW 무시
- 해결: Prompt 간소화, RAW 우선순위, 품질 검증
- 교훈: DB가 문맥 제공, Prompt는 방향만
- 다음: JBody 재테스트

---

## 🚀 즉시 구현 가능한 다음 단계

### 우선순위 1: 문서 관리 백엔드 완성
**현재 상태**: UI 완성 (document_manager.html), API 미구현

**필요 작업**:
1. `/api/v2/documents/` - 문서 검색 API
2. `/api/v2/combine/` - 선택 문서 AI 정리
3. `/api/v2/regenerate/` - 재생성 API
4. 라우트 추가 (`config/urls.py`)

### 우선순위 2: 밈 시나리오 생성 프로토타입
**새로운 기능**

**필요 작업**:
1. `api/api/meme_generator.py` 생성
2. FINAL → 밈 시나리오 변환 로직
3. 시나리오 저장 (`projects/{id}/meme_scenarios/`)
4. 편집 UI (`templates/meme_scenario_editor.html`)

### 우선순위 3: 이미지 생성 API 연동
**외부 서비스 통합**

**필요 작업**:
1. DALL-E 또는 Stable Diffusion API 연동
2. 이미지 설명 → 프롬프트 최적화
3. 생성 이미지 저장 (`meme_images/`)
4. 미리보기 시스템

---

## 🎯 성공 지표

### 단기 (1개월)
- ✅ RAW → DRAFT → FINAL 파이프라인 안정화
- ✅ AI 분석 품질 80점 이상 유지
- 🔄 문서 관리 백엔드 완성
- 🔄 밈 시나리오 첫 프로토타입

### 중기 (3개월)
- 밈 이미지 자동 생성
- 이미지/자막 합성 파이프라인
- 숏 영상 첫 샘플 제작

### 장기 (6개월)
- 전자책 자동 생성 시스템
- 멀티플랫폼 배포 자동화
- One Source Multi Use 완전 구현

---

## 💡 핵심 철학

### J님의 비전
> "RAW 데이터 정리 성공해서 draft나 final로 옮기면, 그 내용으로 밈 시나리오 만들고, 확정되면 밈이미지와 밈자막 제작 후 합성, 그걸로 숏 만들고, 최후로 전자책 완성"

### JNext의 역할
- **실험실**: 모든 새로운 기능 프로토타입
- **중앙 관리**: Firestore 데이터 통제
- **자동화 엔진**: 메서드 개발 후 독립 앱 배포

### AI의 역할
- **증폭기**: J님의 아이디어를 확장
- **보조**: 주인공은 J님, AI는 도구
- **창의성**: 문맥은 DB가 제공, AI는 자유롭게

---

## 📞 다음 Claude에게

이 파일을 먼저 읽으세요.

1. **`docs/claude.md`** - 기본 규칙, J님 호칭, 작업 스타일
2. **`docs/JNEXT_ROADMAP.md`** (이 파일) - 전체 비전, 현재 진행 상황
3. **`docs/conversation_XXX.md`** - 최근 대화 기록

J님은 명확하고 직접적입니다. 
불필요한 설명 없이, 핵심만 전달하세요.
백업 먼저, 구현 후 테스트, 문제 생기면 끝까지 해결.

화이팅! 🚀

---

**작성자**: Claude (클로)  
**작성일**: 2026-01-14 22:00  
**버전**: 1.0
