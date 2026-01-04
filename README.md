# JNext

AI가 직접 DB를 제어하는 시스템 - Django Backend + Firebase Firestore

## 프로젝트 구조

```
JNext/
├── backend/                    # Django 백엔드
│   ├── config/                # Django 설정
│   ├── api/                   # API 앱
│   └── README.md             # 백엔드 상세 가이드
└── jnext-service-account.json # Firebase 키 (Git 제외)
```

## 빠른 시작

### 1. 백엔드 서버 실행

```bash
cd backend
.\venv\Scripts\Activate.ps1
python manage.py runserver
```

### 2. Firebase 설정

1. Firebase Console에서 서비스 계정 키 다운로드
2. `jnext-service-account.json`으로 저장
3. JNext 루트 폴더에 배치

### 3. API 테스트

- http://localhost:8000/ - API 정보
- http://localhost:8000/api/test/ - Firebase 연결 테스트
- http://localhost:8000/api/logs/ - System logs 조회

## 기술 스택

- **Backend**: Django 6.0
- **Database**: Firebase Firestore
- **Python**: 3.14

## 보안

⚠️ **절대 커밋하지 말 것:**
- `*-service-account.json`
- `.env` 파일

## 개발자

J님 & Claude

## 라이선스

Private
