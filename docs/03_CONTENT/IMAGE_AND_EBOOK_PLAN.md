# 전자책 출판 준비 계획
**날짜**: 2026-01-15  
**목표**: FINAL 문서 → 전자책 출판 품질 확보

---

## 1. 현재 상태
✅ **완료된 작업**:
- FINAL 이동 기능 구현 (`/api/v2/documents/move-to-final/`)
- RAW/DRAFT → FINAL 문서 이동 시 자동으로 밈/숏/전자책 필드 추가
- 문서 관리 페이지에서 "➡️ FINAL 이동" 버튼 작동

🔄 **진행 중**:
- 전자책 출판용 폰트/서식 적용
- 이론/설명용 이미지 생성 시스템

---

## 2. 전자책 출판 요구사항

### 2.1 폰트 및 서식
**전자책 가독성 최적화**:
- **본문 폰트**: 나눔명조 / 본명조 (14-16px)
- **제목 폰트**: 나눔고딕 / 본고딕 (20-24px)
- **줄간격**: 1.8-2.0 (출판 표준)
- **문단 간격**: 15-20px
- **여백**: 충분한 패딩 (좌우 30-40px)

**적용 위치**:
- 문서 관리 페이지 미리보기 패널
- 재생성 미리보기 (수정 가능 textarea)
- 최종 FINAL 문서 뷰어

### 2.2 이미지 시스템
**두 가지 이미지 타입 구분**:

#### A. 밈 이미지 (3인 시트콤)
- **캐릭터**: J, 아내, 지피티
- **기본 이미지**: `meme_images/` 폴더에 저장됨
  - J 이미지: ✅ 마음에 듦
  - 아내 이미지 (커트머리/긴머리): ✅ 마음에 듦
  - 지피티 이미지: ❌ 교체 필요
- **생성 방식**: 기본 캐릭터 이미지 + 표정/동작만 변경
- **용도**: 밈스토리 4프레임 (훅/전개/반전/클로징)

#### B. 이론/설명 이미지 (전자책용)
- **용도**: 딱딱한 이론 설명, 동작 다이어그램, 해부학 그림
- **생성 방식**: 
  - Gemini Imagen API 사용
  - 프롬프트 기반 생성 (예: "골반 돌리기 동작 설명 다이어그램")
  - 필요시 J/아내 캐릭터 스타일 참고 가능
- **저장**: Firebase Storage → URL → 마크다운 삽입
- **포맷**: 중앙 정렬 + 캡션

---

## 3. 구현 계획

### Phase 1: 전자책 폰트/서식 적용 (최우선)
**파일**: `api/templates/document_manager.html`

**변경 사항**:
```css
/* 전자책 출판용 폰트 임포트 */
@import url('https://fonts.googleapis.com/css2?family=Nanum+Myeongjo:wght@400;700&family=Nanum+Gothic:wght@400;700&display=swap');

/* 본문 스타일 */
.preview-content, .doc-preview, textarea {
    font-family: 'Nanum Myeongjo', serif;
    font-size: 16px;
    line-height: 2.0;
    padding: 30px 40px;
    color: #333;
}

/* 제목 스타일 */
.preview-title, .doc-title, h1, h2, h3 {
    font-family: 'Nanum Gothic', sans-serif;
    font-weight: 700;
    margin-bottom: 20px;
}

/* 이미지 스타일 */
img {
    max-width: 100%;
    height: auto;
    display: block;
    margin: 20px auto;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

/* 이미지 캡션 */
.image-caption {
    text-align: center;
    font-size: 14px;
    color: #666;
    font-style: italic;
    margin-top: 8px;
}
```

### Phase 2: 이미지 생성 UI 추가
**위치**: 문서 관리 페이지 미리보기 패널

**기능**:
1. **"🎨 이미지 생성" 버튼** (각 문서 뷰어에)
2. **이미지 생성 다이얼로그**:
   ```
   📝 이미지 설명 입력:
   [프롬프트 입력창]
   예: "골반 돌리기 동작 해부학 다이어그램, 근육 강조"
   
   🎨 스타일 선택:
   [ ] 다이어그램 (선명, 교육용)
   [ ] 일러스트 (부드러운, 친근한)
   [ ] 사진 같은 (사실적)
   
   [생성] [취소]
   ```
3. **생성 후 미리보기 → 문서에 삽입**

### Phase 3: 이미지 생성 백엔드 API
**엔드포인트**: `/api/v2/images/generate/`

**기능**:
- Gemini Imagen API 호출
- Firebase Storage 업로드
- 이미지 URL 반환
- 문서에 마크다운 자동 삽입: `![이미지설명](https://...)`

### Phase 4: 캐릭터 이미지 교체 (지피티)
- meme_images 폴더의 지피티 이미지 재생성
- J/아내 스타일과 조화롭게

---

## 4. 기술 스택
- **이미지 생성**: Google Gemini Imagen API
- **이미지 저장**: Firebase Storage
- **폰트**: Nanum Myeongjo (본문), Nanum Gothic (제목)
- **마크다운**: 이미지 삽입 `![alt](url)`

---

## 5. 우선순위
1. ✅ **전자책 폰트/서식 적용** (지금 바로)
2. 🔄 **이미지 생성 UI 구현**
3. 🔄 **이미지 생성 백엔드 API**
4. 📋 **지피티 캐릭터 재생성** (나중에)

---

## 6. 다음 세션 체크리스트
- [ ] 문서 관리 페이지 폰트 적용 확인
- [ ] 이미지 생성 버튼 작동 확인
- [ ] Firebase Storage 권한 설정
- [ ] Gemini Imagen API 활성화
- [ ] 샘플 이미지 생성 테스트
