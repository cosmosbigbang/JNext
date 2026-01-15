# Hino Review 카드 호버 효과 수정 작업

**작성일:** 2026-01-12  
**파일:** backend/templates/hino_review.html  
**현재 버전:** v3.0 FINAL

---

## 📌 문제 정의

**증상:**
- Contents 탭과 원본 탭에서 카드에 마우스를 올리거나 클릭하면:
  - 카드가 커짐 (scale/transform 효과)
  - 다른 카드들이 사라짐
- Draft 탭은 정상 작동

**목표:**
- 호버/클릭 시 카드 크기 변화 없음
- 다른 카드가 사라지지 않음
- 색상/투명도만 변경

---

## ✅ 완료된 작업

### 1. CSS Transform/Box-Shadow 제거

**제거된 효과:**
```css
/* BEFORE (v1.0 - v2.0) */
.stat-card:hover {
  transform: scale(1.15) translateY(-5px);
  box-shadow: 0 15px 40px rgba(102, 126, 234, 0.4);
}

.card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 30px rgba(0,0,0,0.2);
}

.filter-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
}
```

**현재 효과 (v3.0 FINAL):**
```css
/* AFTER - 크기 변화 없이 투명도/색상만 변경 */
.stat-card {
  transition: opacity 0.2s;
}
.stat-card:hover {
  opacity: 0.9;
}

.card {
  transition: border-color 0.2s;
}
.card:hover {
  border-color: #667eea;
}
```

### 2. 백업 생성
- `backend/templates/hino_review_backup_v3.0_FINAL_20260112.html`

---

## ❌ 현재 문제

**상황:**
- CSS 수정 완료했지만 Contents/원본 탭에서 여전히 동일한 증상 발생
- Draft 탭만 정상 작동

**가능한 원인:**
1. **JavaScript가 스타일 오버라이드:**
   - `displayContentStats()` 함수
   - `displayRawStats()` 함수
   - Grid 레이아웃 동적 변경

2. **브라우저 캐싱 문제:**
   - 이미 여러 번 캐시 클리어 시도했으나 효과 없음
   - HAR 파일 분석 필요

---

## 🔧 향후 작업 계획

### Phase 1: 원인 파악 (최우선)

**1-1. JavaScript 코드 점검**
```
대상:
- displayContentStats() 함수
- displayRawStats() 함수  
- filterContentByType() 함수
- filterRawByCategory() 함수

확인 사항:
- Grid 레이아웃 동적 변경 코드
- inline style 강제 적용 여부
- transform/scale 사용 여부
```

**1-2. 브라우저 개발자 도구 확인**
```
확인 항목:
- Contents 탭 .stat-card의 Computed CSS
- transform, box-shadow 속성 적용 여부
- JavaScript에서 추가한 inline style
```

**1-3. Draft vs Contents 차이점 분석**
```
비교:
- Draft 탭 CSS/JavaScript 로직
- Contents 탭 CSS/JavaScript 로직
- 왜 Draft는 되고 Contents는 안 되는지
```

### Phase 2: 해결 방안 적용

**방안 A: 강제 CSS 적용 (!important)**
```css
.stat-card,
.stat-card:hover,
.stat-card.active {
  transform: none !important;
  box-shadow: none !important;
}
```

**방안 B: JavaScript 수정**
```javascript
// displayContentStats/displayRawStats 함수에서
// transform/scale 관련 코드 제거
```

**방안 C: Grid 레이아웃 고정**
```css
.stats-grid {
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)) !important;
}
```

### Phase 3: 테스트 및 검증

1. Draft 탭: 기존 작동 유지 확인
2. Contents 탭: 카드 크기 변화 없음 확인
3. 원본 탭: 카드 크기 변화 없음 확인
4. 모든 브라우저에서 캐시 클리어 후 테스트

---

## 📂 관련 파일

| 파일 경로 | 설명 |
|----------|------|
| `backend/templates/hino_review.html` | 메인 작업 파일 (v3.0 FINAL) |
| `backend/templates/hino_review_backup_v3.0_FINAL_20260112.html` | 백업 파일 |

---

## 🎯 다음 세션 체크리스트

- [ ] JavaScript 코드 점검 (displayContentStats, displayRawStats)
- [ ] 브라우저 개발자 도구로 Computed CSS 확인
- [ ] Draft vs Contents 동작 차이 분석
- [ ] 해결 방안 A/B/C 중 선택하여 적용
- [ ] 전체 탭 테스트

---

## 📝 메모

- Draft 탭이 정상 작동하는 것이 중요한 단서
- CSS만 수정해서는 해결 안 됨 → JavaScript 점검 필수
- Grid 레이아웃이 동적으로 변하면서 카드가 사라지는 것으로 추정

