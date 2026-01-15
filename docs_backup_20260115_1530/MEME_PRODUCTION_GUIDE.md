# 하이노밸런스 밈 제작 프로세스 (중요!)

**작성일**: 2026-01-14  
**작성자**: J님 직접 설명  
**프로젝트**: 하이노밸런스 전용 (JNext 범용 아님!)

---

## 🎨 밈 제작 핵심 원칙

### 기본 이미지 (JNext/meme_images/)

**중요**: 이 이미지들은 **하이노밸런스 프로젝트 전용**입니다.

**J님 (나)**: 코수염 캐릭터  
**아내**: 
- 커트머리 버전
- 긴머리 버전

**핵심**: 얼굴은 똑같이, 동작 표현만 다시 그림

---

## 🔧 밈 제작 워크플로우

### 문제점
- 밈에 한글 자막 직접 삽입 시 계속 오류 발생

### 해결 방안 (일괄 작업)

```
1단계: 밈 자막 제작
├─ 한글 자막 텍스트만 별도 생성
├─ 폰트, 크기, 위치 지정
└─ 자막 레이어 파일 저장

2단계: 밈 이미지 제작  
├─ 기존 캐릭터 이미지 불러오기
│  ├─ J님 (코수염)
│  └─ 아내 (커트머리/긴머리)
├─ 얼굴은 그대로 유지
├─ 동작/표정만 수정
└─ 이미지 레이어 파일 저장

3단계: 통합
├─ 자막 레이어 + 이미지 레이어 합성
├─ 최종 밈 이미지 출력
└─ PNG/JPG 저장
```

---

## 📁 파일 구조

```
JNext/
├── meme_images/                    # 하이노밸런스 전용 캐릭터 이미지
│   ├── J_코수염.png               # J님 기본 이미지 (하이노용)
│   ├── 아내_커트머리.png           # 아내 커트 기본 (하이노용)
│   ├── 아내_긴머리.png             # 아내 긴머리 기본 (하이노용)
│   └── KakaoTalk_*.png            # 기존 하이노 밈 이미지들
│
└── backend/
    └── api/
        ├── meme_generator.py       # 밈 생성 로직 (범용)
        └── projects/
            └── hinobalance.py      # 하이노밸런스 프로젝트 설정
```

**주의**: 다른 프로젝트(ExamNavi, JBody 등)는 각자 별도 캐릭터 이미지 필요

---

## 🎯 Temperature 설정 (Final 단계)

### 전자책
- 목적: 확정된 Draft → 그대로 출력
- Temperature: 낮음 (0.2-0.3)
- 창의성: 불필요

### 밈, 밈이미지, 숏, 앱
- 목적: 창작물 제작
- Temperature: 높음 (0.6-0.7)
- 창의성: 필수

---

## 🔄 JNext 3단계 Temperature 최적값

### RAW (대화 모드)
```python
temperature: 0.7 (고정)  # 창의 최고
목적: 아이디어 증폭
```

### DRAFT (정리 모드)
```python
temperature: 0.5~0.55    # 균형
목적: 구조화, 카테고리 확정
슬라이더: DB 양 조절
```

### FINAL (상품화 모드)
```python
# 유형별 차등 적용
전자책: 0.2-0.3 (정확)
밈/숏/앱: 0.6-0.7 (창의)
```

---

## 💡 밈 제작 자동화 로직

```python
# backend/api/meme_generator.py

class MemeGenerator:
    """
    밈 제작 3단계 프로세스
    """
    
    def generate_meme(scenario_text):
        """
        Args:
            scenario_text: 밈 시나리오 (DRAFT에서 생성)
        
        Returns:
            {
                'caption_layer': '자막 레이어 파일',
                'image_layer': '이미지 레이어 파일',
                'final_meme': '통합 밈 이미지'
            }
        """
        
        # 1. 자막 제작 (한글 오류 방지)
        caption = create_caption_layer(
            text=scenario_text,
            font='NanumGothicBold',
            size=48
        )
        
        # 2. 이미지 제작 (캐릭터 재사용)
        image = create_character_scene(
            base_character='J_코수염.png',  # 얼굴 동일
            action='손가락 가리키기',         # 동작만 변경
            expression='웃는 표정'
        )
        
        # 3. 통합
        final_meme = merge_layers(caption, image)
        
        return final_meme
```

---

## 📝 중요 노트

**전 Claude가 남긴 정보:**
- `backend/api/meme_generator.py` 파일 존재 (369 lines)
- DALL-E 3 활용한 캐릭터 생성 로직 있음
- Pillow 기반 자막 합성 로직 있음

**현재 상태:**
- 기본 캐릭터 이미지 13개 존재 (meme_images/)
- 자막/이미지 분리 작업 구현 필요
- 통합 프로세스 자동화 필요

---

**저장 위치**: `c:\Projects\JNext\MEME_PRODUCTION_GUIDE.md`
**참조**: `backend/api/meme_generator.py`, `JNEXT_CORE_VISION.md`
