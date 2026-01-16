# JNext Backend Setup Guide

## 프로젝트 구조

```
JNext/
├── api/                        # Django Backend
│   ├── venv/                   # Python 가상환경
│   ├── config/                 # Django 프로젝트 설정
│   │   ├── settings.py        # Firebase 초기화 포함
│   │   ├── urls.py            # API 라우팅
│   │   └── wsgi.py
│   ├── api/                   # API 앱
│   │   ├── views.py          # API 엔드포인트
│   │   ├── views_v2.py       # v2 채팅 API
│   │   ├── ai_config.py      # AI 설정 중앙 관리
│   │   └── projects/         # 프로젝트별 설정
│   │       └── hinobalance.py
│   ├── scripts/              # 범용 유틸리티
│   │   ├── check/           # DB 상태 확인 스크립트
│   │   ├── test/            # API 테스트 스크립트
│   │   └── utils/           # 기타 유틸리티
│   ├── manage.py            # Django 관리 명령
│   ├── requirements.txt     # Python 패키지 목록
│   └── .env                 # 환경 변수 (Git 제외)
│
├── projects/                 # 프로젝트별 데이터/스크립트
│   └── hinobalance/         # 하이노밸런스 프로젝트
│       ├── data/            # 원본 데이터
│       │   ├── theory/      # 카테고리별 이론
│       │   ├── exercises/   # 개별 운동 설명
│       │   └── combined/    # 통합 이론 문서
│       ├── scripts/         # 전용 스크립트
│       │   ├── analyze.py
│       │   ├── publishing.py
│       │   ├── upload/      # Firestore 업로드
│       │   └── organize/    # 데이터 정리
│       └── docs/            # 프로젝트 문서
│
└── jnext-service-account.json  # Firebase 서비스 계정 키 (Git 제외)
```

## 설치된 패키지

- Django 6.0
- python-dotenv (환경 변수 관리)
- firebase-admin (Firebase 연동)

## Firebase 설정

### 1. 서비스 계정 키 준비
1. Firebase Console (https://console.firebase.google.com) 접속
2. 프로젝트 설정 → 서비스 계정
3. "새 비공개 키 생성" 클릭
4. 다운로드된 JSON 파일을 `jnext-service-account.json`으로 이름 변경
5. **JNext 루트 폴더**에 저장 (또는 backend 폴더)

### 2. 환경 변수 확인
`.env` 파일에 다음 내용이 설정되어 있습니다:
```
FIREBASE_CREDENTIALS_PATH=jnext-service-account.json
```

## 실행 방법

### 터미널 명령어 (순서대로 실행)

```powershell
# 1. backend 폴더로 이동
cd C:\Projects\JNext\backend

# 2. 가상환경 활성화
.\venv\Scripts\Activate.ps1

# 3. Django 마이그레이션 (데이터베이스 초기화)
python manage.py migrate

# 4. Django 개발 서버 실행
python manage.py runserver
```

## API 엔드포인트

서버 실행 후 브라우저에서 접속:

### 1. 인덱스 (http://localhost:8000/)
- API 정보 및 엔드포인트 목록 표시

### 2. Firebase 연결 테스트 (http://localhost:8000/api/test/)
- Firestore의 `system_logs` 컬렉션에 테스트 데이터 추가
- 응답 예시:
```json
{
  "status": "success",
  "message": "Firebase 연결 성공! system_logs에 데이터가 추가되었습니다.",
  "document_id": "abc123...",
  "data": {
    "status": "JNext System Initialized",
    "timestamp": "2026-01-03T19:45:00.123456",
    "source": "JNext Backend API",
    "message": "Firebase Firestore 연결 테스트 성공"
  }
}
```

### 3. System Logs 조회 (http://localhost:8000/api/logs/)
- Firestore의 `system_logs` 컬렉션에서 최근 50개 로그 조회

### 4. Django Admin (http://localhost:8000/admin/)
- Django 관리자 패널 (슈퍼유저 생성 필요)

## 추가 작업 (옵션)

### 슈퍼유저 생성 (Admin 패널 사용 시)
```powershell
python manage.py createsuperuser
```

### 패키지 추가 설치 시
```powershell
# 가상환경 활성화 후
pip install <패키지명>

# requirements.txt 업데이트
pip freeze > requirements.txt
```

## 문제 해결

### Firebase 초기화 실패 시
1. `jnext-service-account.json` 파일이 올바른 위치에 있는지 확인
2. 서버 시작 시 콘솔 메시지 확인:
   - 성공: `[JNext] Firebase initialized successfully`
   - 실패: `[JNext] Firebase initialization failed: ...`
3. Firebase Console에서 Firestore 활성화 확인

### 가상환경 활성화 오류 시
PowerShell 실행 정책 변경:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## 다음 단계

1. ✅ Firebase 연결 테스트 (`/api/test/`)
2. ✅ Firestore Console에서 `system_logs` 컬렉션 확인
3. 추가 API 엔드포인트 개발
4. AI 에이전트를 통한 DB 제어 기능 구현
