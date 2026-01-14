# JNext 프로젝트 가이드 for Claude

안녕하세요, 클로드님. JNext 프로젝트에 참여하시는 것을 환영합니다. 이 문서는 프로젝트의 구조를 빠르게 파악하고, 발생할 수 있는 일반적인 문제들을 해결하는 데 도움을 주기 위해 작성되었습니다.

## 1. JNext 프로젝트 핵심 구조

JNext는 **AI 기반 콘텐츠 제공 플랫폼**으로, 크게 3개의 파트로 구성됩니다.

1.  **백엔드 (Django - `backend/`)**:
    *   **역할**: 데이터 처리, AI 연동, API 제공의 중심 허브입니다.
    *   **데이터 저장**: Firebase Firestore (주 데이터베이스) + `db.sqlite3` (로컬용)
    *   **핵심 디렉토리**:
        *   `api/`: 모바일 앱과 통신하는 REST API 로직이 담겨 있습니다. (`views.py`, `views_v2.py`, `urls.py`가 핵심입니다.)
        *   `config/`: Django 프로젝트 설정 (`settings.py`) 및 URL 라우팅의 시작점 (`urls.py`) 입니다.
    *   **주요 스크립트 그룹**:
        *   **데이터 수집/가공**: `upload_*.py`, `organize_*.py`, `create_*.py` 등은 `.txt` 원본 파일을 읽어 Firestore에 저장하는 역할을 합니다.
        *   **AI 연동**: `api/ai_service.py`, `content_generator.py` 등에서 Gemini, GPT, Claude API를 직접 호출합니다.
        *   **유지보수**: 루트 레벨의 `check_*.py`, `delete_*.py` 등은 DB 상태 확인 및 정리를 위한 일회성 스크립트입니다.

2.  **모바일 앱 (Flutter)**:
    *   `hinobalance_mobile/`
    *   `jnext_mobile/`
    *   백엔드에서 제공하는 API를 사용하여 사용자에게 맞춤형 콘텐츠를 보여주는 클라이언트입니다.

3.  **배포**:
    *   `render.yaml`: Render.com을 이용한 자동 배포 설정 파일입니다. `git push` 시 자동으로 배포가 진행될 수 있습니다.

## 2. 일반적인 문제 및 디버깅 팁

JNext 개발 중에는 다음과 같은 문제들이 자주 발생할 수 있습니다.

### **문제 1: API를 수정했는데도 이전처럼 동작합니다.**

가장 흔하게 겪는 문제입니다. (예: `GEMINI_API_ISSUE`)

*   **원인**: Django 개발 서버(`runserver`)가 코드 변경을 제대로 감지하지 못하고, 메모리에 남아있는 이전 버전의 코드를 계속 실행하기 때문입니다.
*   **해결 절차**:
    1.  **프로세스 완전 종료**: `Ctrl+C`로 서버를 종료한 후, 포트(`8000`)가 계속 사용 중인지 확인하세요. (PowerShell: `Get-NetTCPConnection -LocalPort 8000`) 좀비 프로세스가 있다면 강제 종료(`Stop-Process -Id <ID> -Force`)해야 합니다.
    2.  **파이썬 캐시 삭제**: `backend/` 폴더 내의 모든 `__pycache__` 디렉토리를 삭제하세요. 오래된 컴파일 코드가 문제를 일으킬 수 있습니다.
    3.  **서버 재시작**: 위 두 단계를 거친 후 서버를 재시작하세요.

### **문제 2: API가 `400 Bad Request` 또는 예상치 못한 오류를 반환합니다.**

*   **원인**: API 요청이 내가 수정한 코드가 아닌, 다른 곳에 있는 **옛날 코드**로 전달되고 있을 가능성이 매우 높습니다.
*   **해결 절차 (URL 라우팅 추적)**:
    1.  **시작점**: `backend/config/urls.py` 파일에서 요청한 URL(예: `/api/v2/chat/`)이 어떤 `include()`로 연결되는지 확인합니다.
    2.  **중간점**: `backend/api/urls.py` 파일로 이동하여, 해당 URL이 최종적으로 어떤 **뷰(View)** 클래스 또는 함수(예: `views_v2.ChatView`)에 연결되는지 찾습니다.
    3.  **종착점**: 해당 뷰 파일(`views_v2.py`)을 열어, 그 안의 코드가 정말 최신 로직(예: `ai_service.py`의 함수)을 호출하는지, 아니면 자체적으로 구식 API 호출 코드를 가지고 있는지 확인합니다.

### **문제 3: 여러 AI 모델 SDK 간의 충돌**

*   **특징**: JNext는 Gemini, GPT, Claude 등 여러 AI를 사용하므로, 각 SDK의 고유한 초기화 방식과 파라미터 형식을 주의해야 합니다.
*   **디버깅 팁**:
    *   **Gemini**: `generate_content`의 `config` 파라미터는 딕셔너리가 아닌 `types.GenerateContentConfig` 객체를 사용해야 합니다.
    *   **Claude**: `proxies` 인자 관련 오류가 발생할 수 있으니, 초기화 코드를 주의 깊게 살펴보세요.
    *   각 AI 서비스(`ai_service.py` 등)가 올바른 클라이언트와 설정을 사용하는지 교차 확인하는 것이 중요합니다.

이 가이드가 JNext 프로젝트 개발에 도움이 되기를 바랍니다. 막히는 부분이 있다면 이 문서를 다시 참고해 보세요.
