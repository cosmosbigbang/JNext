# 하이노밸런스 카테고리 구조 및 자동화 전략

## 핵심 개념

**카테고리 분류 = 앱 메뉴 구조**

카테고리를 정확히 지정하면, 그것이 바로 앱의 메뉴가 되는 자동화 시스템입니다.

## 작업 플로우

```
RAW (원본) 
  ↓ [카테고리 분류 - 핵심!]
DRAFT (초안)
  ↓ [검토 및 정제]
FINAL (최종본)
  ↓ [SQL 쿼리]
앱 메뉴 자동 생성
```

## 표준 카테고리 구조

### 1. 이론
- `하이노이론-요약`
- `하이노이론-중간`
- `하이노이론-전체`
- `하이노이론-가치`

### 2. 실전
- `하이노워밍`
- `하이노골반`
- `하이노워킹`
- `하이노스케이팅`
- `하이노풋삽`
- `하이노철봉`

### 3. 밈
- `하이노밈`

### 4. 숏
- `하이노숏`

## Raw → Draft 작업 시 주의사항

### ✅ 올바른 카테고리 지정 예시

```python
{
    "카테고리": "하이노워킹",
    "제목": "하이노워킹 전진",
    "내용": "..."
}
```

```python
{
    "카테고리": "하이노이론-요약",
    "제목": "균형의 원리",
    "내용": "..."
}
```

### ❌ 잘못된 카테고리 예시

```python
{
    "카테고리": "이론",  # 너무 모호함
    "카테고리": "운동",  # 구체적이지 않음
    "카테고리": "하이노", # 카테고리 미분류
}
```

## 자동화 SQL 예시

```sql
-- 메뉴 자동 생성
SELECT DISTINCT 카테고리 
FROM hino_final 
ORDER BY 카테고리;

-- 카테고리별 콘텐츠 조회
SELECT * 
FROM hino_final 
WHERE 카테고리 = '하이노워킹'
ORDER BY created_at DESC;
```

## Firebase 컬렉션 구조

```
hino_raw/           # 원본 (카테고리 미지정 가능)
  └─ 문서들

hino_draft/         # 초안 (카테고리 필수!)
  └─ 문서들
      ├─ 카테고리: "하이노워킹"
      ├─ 제목: "..."
      └─ 내용: "..."

hino_final/         # 최종본 (카테고리 검증 완료)
  └─ 문서들
      ├─ 카테고리: "하이노워킹"
      ├─ 제목: "..."
      └─ 내용: "..."
```

## 앱 메뉴 자동 생성 로직

```python
# 카테고리 기반 메뉴 구조 생성
def generate_menu_structure(collection='hino_final'):
    db = firestore.client()
    docs = db.collection(collection).stream()
    
    categories = set()
    for doc in docs:
        category = doc.to_dict().get('카테고리')
        if category:
            categories.add(category)
    
    # 카테고리를 메뉴로 변환
    menu = {
        '이론': [],
        '실전': [],
        '밈': [],
        '숏': []
    }
    
    for cat in sorted(categories):
        if cat.startswith('하이노이론'):
            menu['이론'].append(cat)
        elif cat.startswith('하이노') and not cat.startswith('하이노이론'):
            menu['실전'].append(cat)
        elif '밈' in cat:
            menu['밈'].append(cat)
        elif '숏' in cat:
            menu['숏'].append(cat)
    
    return menu
```

## 이점

1. **자동화**: 카테고리만 정확히 지정하면 메뉴가 자동 생성
2. **일관성**: 표준 카테고리 구조로 혼란 방지
3. **확장성**: 새 카테고리 추가 시 앱 메뉴 자동 반영
4. **유지보수**: SQL 쿼리만으로 메뉴 관리 가능

## 앞으로의 작업 원칙

### Raw → Draft 작업 시
1. 내용을 읽고 **정확한 카테고리** 지정
2. 표준 카테고리 구조 준수
3. 애매하면 가장 가까운 카테고리 선택

### Draft → Final 작업 시
1. 카테고리 정확성 재검증
2. 제목과 내용 정제
3. 중복 제거

### 결과
**카테고리 잘 만들면 → SQL 쿼리 → 메뉴 자동 생성 → 이론 혼란 없음!** ✅

---

작성일: 2026-01-13  
작성자: J님, Claude
